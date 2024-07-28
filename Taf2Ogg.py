#!/bin/python3

import sys
import struct
import re 
import ffmpeg
import os 
from google.protobuf import descriptor_pb2, descriptor_pool, message_factory

# Protobuf definition in descriptor form
file_descriptor_proto = descriptor_pb2.FileDescriptorProto()
file_descriptor_proto.name = 'tonie_header.proto'
file_descriptor_proto.package = 'tonie'
file_descriptor_proto.syntax = 'proto3'

# TonieHeader message type
message_descriptor_proto = file_descriptor_proto.message_type.add()
message_descriptor_proto.name = 'TonieHeader'

# Fields of TonieHeader
field_data_hash = message_descriptor_proto.field.add()
field_data_hash.name = 'dataHash'
field_data_hash.number = 1
field_data_hash.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field_data_hash.type = descriptor_pb2.FieldDescriptorProto.TYPE_BYTES

field_data_length = message_descriptor_proto.field.add()
field_data_length.name = 'dataLength'
field_data_length.number = 2
field_data_length.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field_data_length.type = descriptor_pb2.FieldDescriptorProto.TYPE_UINT32

field_timestamp = message_descriptor_proto.field.add()
field_timestamp.name = 'timestamp'
field_timestamp.number = 3
field_timestamp.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field_timestamp.type = descriptor_pb2.FieldDescriptorProto.TYPE_UINT32

field_chapter_pages = message_descriptor_proto.field.add()
field_chapter_pages.name = 'chapterPages'
field_chapter_pages.number = 4
field_chapter_pages.label = descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED
field_chapter_pages.type = descriptor_pb2.FieldDescriptorProto.TYPE_UINT32
field_chapter_pages.options.packed = True

field_padding = message_descriptor_proto.field.add()
field_padding.name = 'padding'
field_padding.number = 5
field_padding.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field_padding.type = descriptor_pb2.FieldDescriptorProto.TYPE_BYTES

# Create a pool and add the FileDescriptorProto
pool = descriptor_pool.DescriptorPool()
file_descriptor = pool.Add(file_descriptor_proto)

# Get the message descriptor and create a message class
message_descriptor = pool.FindMessageTypeByName('tonie.TonieHeader')
TonieHeader = message_factory.GetMessageClass(message_descriptor)

def ExtractChapters(filename):
    with open(filename, 'rb') as f:
        # Read the first 4096 bytes which includes the header
        header_data = f.read(0x1000)

        # Decode the header
        header = TonieHeader()
        header.ParseFromString(header_data[4:])

        return list(header.chapterPages)


def read_and_save_binary_file_bytes(input_filename, output_filename, ChapterList):
    try:
        with open(input_filename, 'rb') as f:
            # Save the bytes to the output file
            try:
                with open(output_filename, 'wb') as output_file:
                    i = 0
                    TimeList = list((""))
                    f.seek(0)
                    counter = 0 
                    print("Scanning file for Chapters...")
                    while True:
                        bytes_data = f.read(4096)
                        if i > 0:
                            output_file.write(bytes_data)
                        i +=1
                        if not bytes_data:
                            break
                        index = bytes_data.find(b"OggS")

                        if index != -1:
                            buf = bytes_data[index+6:index+22]
                            granule_pos = int.from_bytes(buf[:7], byteorder='little')
                            time_seconds = granule_pos / 48000 # 48000 = sample rate for opus
                            seq_num = int.from_bytes(buf[12:18], byteorder='little')
                            if seq_num == ChapterList[counter]:
                                print(f"Found {counter} of {len(ChapterList)-1}",end="\r")
                                TimeList.append(f"{int(time_seconds // 3600):02}:{int((time_seconds % 3600) // 60):02}:{(time_seconds % 60):02.03f}")
                                counter +=1
                                if counter >= len(ChapterList):
                                    print(f"Found {counter-1} of {len(ChapterList)-1}")
                                    break
                    if counter < len(ChapterList):
                        print("Your Toniebox has not Cached the entire file. \nExtraction of all Chapters may not be possible.")
                    print(f"Scanning Complete.")
                    return TimeList
            except FileNotFoundError:
                print(f"File {output_filename} not found.")
            except Exception as e:
                print(f"An error occurred: {e}")
    
    except FileNotFoundError:
        print(f"File {input_filename} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def split_audio(input_file, chapter_list, output_dir):
    print("Extracting files...")
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            print(f"Failed to create output directory: {e}")
            return

    length = len(chapter_list)
    for i in range(1, length):
        print(f"Exporting file {i} of {length-1}",end="\r")
        start_time = chapter_list[i-1]
        end_time = chapter_list[i]
        output_file = os.path.join(output_dir, f"Chapter_{i}.ogg")
        try:
            (
            ffmpeg
            .input(input_file, ss=start_time, to=end_time, v=8)
            .output(output_file, codec='copy')
            .run()
            )
        except ffmpeg.Error as e:
            print(f"Error exporting file {output_file}: {e}")
    print("\ndone")
        
def main(filename, output_dir):
    try:
        output_filename = os.path.join('/tmp', os.path.basename(filename) + ".ogg")
        TimeList = read_and_save_binary_file_bytes(filename, output_filename, ExtractChapters(filename))
        split_audio(output_filename, TimeList, output_dir)
        os.remove(output_filename)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <tonie_file> <output_directory>")
        sys.exit(1)
    
    filename = sys.argv[1]
    output_dir = sys.argv[2]
    main(filename, output_dir)
