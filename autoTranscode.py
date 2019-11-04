import ffmpeg
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


# Following are a bunch of helper functions to wrap into a "try" "except" loop
# They all generate exif data to add to our naming convention


def get_bit_depth(exif_data):
    return str(exif_data["streams"][0]["bits_per_raw_sample"]) + "bit"


def get_height_width(exif_data):
    return (
        str(exif_data["streams"][0]["coded_height"])
        + "x"
        + str(exif_data["streams"][0]["coded_width"])
    )


def get_creation_time(exif_data):
    return pendulum.parse(
        exif_data["streams"][0]["tags"]["creation_time"]
    ).to_date_string()


def generate_name(file, extension):
    """Function to generate name based on exif data

    Arguments:
        file {PosixPath} -- path to file
        extension {string} -- string of extension

    Returns:
        String -- new path for the file!
    """
    old_name = file.stem
    # Adjust parents based on folder structure
    project_name = str(file.parents[1])

    # Grabbing metadata
    exif_data = ffmpeg.probe(str(file))
    getter_pairs = [get_bit_depth, get_height_width, get_creation_time]
    getter_dictionary = dict()
    # Mapping metadata to corresponding name in dict
    for getter in getter_pairs:
        mapped_name = getter.__name__.split("_", 1)[1]
        try:
            getter_dictionary[mapped_name] = getter(exif_data)
        except KeyError:
            getter_dictionary[mapped_name] = "NA"

    name_list = [
        project_name,
        old_name,
        getter_dictionary["bit_depth"],
        getter_dictionary["height_width"],
        getter_dictionary["creation_time"],
    ]
    new_name = "_".join(name_list) + extension
    new_name = file.parent / new_name
    return str(new_name)


def batch_convert(project_directory):
    project_directory = Path(project_directory)
    media_directory = project_directory / "media"
    old_directory = media_directory / "old"
    file_list = list_dir(media_directory)
    for file in file_list:
        try:
            if any(str(file).split("_")[1] in str(s) for s in file_list):
                print("{} already processed. Continuing..".format(str(file)))
                continue
        except IndexError:
            pass
        file_name = generate_name(file, ".mov")
        stream = ffmpeg.input(str(file))
        stream = ffmpeg.output(stream, file_name, vcodec="prores")
        ffmpeg.run(stream)
        destination = old_directory / file.name
        try:
            with destination.open(mode="xb") as fid:
                fid.write(file.read_bytes())
            file.unlink()
        except FileExistsError:
            print(
                "file did not move correctly, refer to "
                "{}/log/file_move_error.log".format(str(media_directory))
            )


batch_convert("sampleProject")

# TODO: Check /media/old for base filename before continuing
# TODO: Set up folder watching system (probably watchdog)
# TODO: Potentially make list of processed files as fallback?
