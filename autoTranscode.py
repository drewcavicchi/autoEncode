import ffmpeg
import json
import pendulum
from pathlib import Path


def list_dir(mypath):
    """Quick function to return all files in a directory

    Arguments:
        mypath {String} -- string of relative path

    Returns:
        PosixPath -- PosixPath of file, can be further manipulated
    """
    converted_path = Path(mypath)
    onlyfiles = [f for f in converted_path.iterdir() if f.is_file()]
    return onlyfiles

# Following are a bunch of helper functions to wrap into a "try" "execpt" loop


def get_bit_depth(exif_data):
    return str(exif_data['streams'][0]['bits_per_raw_sample']) + "bit"


def get_height_width(exif_data):
    return str(exif_data['streams'][0]['coded_height']) + "x" + str(exif_data['streams'][0]['coded_width'])


def get_creation_time(exif_data):
    return pendulum.parse(exif_data['streams'][0]['tags']['creation_time']).to_date_string()


def generate_name(file, extension):
    """Function to generate name based on exif data

    Arguments:
        file {PosixPath} -- path to file
        extension {string} -- string of extension

    Returns:
        String -- new path for the file!
    """
    old_name = file.stem
    exif_data = ffmpeg.probe(str(file))
    getter_pairs = [get_bit_depth, get_height_width, get_creation_time]
    getter_dictionary = dict()
    for getter in getter_pairs:
        try:
            getter_dictionary[getter.__name__.split(
                "_", 1)[1]] = getter(exif_data)
        except:
            getter_dictionary[getter.__name__.split("_", 1)[1]] = "NA"

    name_list = [old_name, getter_dictionary['bit_depth'],
                 getter_dictionary['height_width'], getter_dictionary['creation_time']]
    new_name = "_".join(name_list)+extension
    new_name = file.parent/new_name
    return str(new_name)


def batch_convert(project_directory):
    project_directory = Path(project_directory)
    media_directory = project_directory/"media"
    old_directory = media_directory/"old"
    for file in list_dir(media_directory):
        old_dir = Path()
        stream = ffmpeg.input(str(file))
        stream = ffmpeg.output(stream, generate_name(
            file, ".mov"), vcodec='prores')
        ffmpeg.run(stream)
        destination = old_directory / file.name
        try:
            with destination.open(mode='xb') as fid:
                fid.write(file.read_bytes())
            file.unlink()
        except:
            print("file did not move correctly, refer to {}/log/file_move_error_log.log".format(str(media_directory)))


batch_convert('sampleProject')

# directory_path = "sampleProject/media"

# exif_data = ffmpeg.probe('test_1.MP4')

# bit_depth = str(exif_data['streams'][0]['bits_per_raw_sample']) + "bit"
# height_width = str(exif_data['streams'][0]['coded_height']) + "x" + str(exif_data['streams'][0]['coded_width'])
# creation_time = pendulum.parse(exif_data['streams'][0]['tags']['creation_time']).to_date_string()
# print(type(creation_time))
# print(bit_depth, aspect_ratio, height_width, creation_time)
# print(exif_data['streams'][0],
# exif_data['streams'][0],
# exif_data['streams'][0],
# exif_data['streams'][0])

# stream = ffmpeg.input('test_1.MP4')
# stream = ffmpeg.output(stream, 'output.mov', vcodec='prores')
# ffmpeg.run(stream)
