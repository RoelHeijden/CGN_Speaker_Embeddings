import os
import json

from data_processing import DataProcessing
from segmentation import Segmentation
from embedding import Embedding


def main():
    # data paths
    sub_folder = 'comp-d\\nl\\'  # d and c are the maps with the telephone conversations
    data_path = 'data\\audio\\wav\\' + sub_folder
    labels_path = 'data\\annot\\text\\ort\\' + sub_folder
    data_out_path = 'processed_data\\embeddings_comp-d_nl\\'

    # init classes
    dp = DataProcessing(max_n_files=-1)
    segma = Segmentation()
    embed = Embedding()

    # check the amount of files in each folder
    files_check(folder_paths=[data_path, labels_path])

    # load dataset
    dataset = dp.load_dataset(folder_path=data_path)

    # load dataset labels
    speaker_labels = dp.load_speaker_labels(folder_path=labels_path)

    # segment dataset in speaker turns
    segments_dataset = segma.segment_dataset(dataset=dataset, labels=speaker_labels)

    # create embeddings
    embeddings_dataset = embed.create_embeddings(dataset=segments_dataset)

    # write out embeddings_dataset to file
    write_out_dataset(embeddings_dataset, folder_out=data_out_path)


def write_out_dataset(dataset, folder_out):
    output_file = folder_out + 'embeddings.json'
    with open(output_file, 'w') as f:
        for element in dataset:
            json.dump(element, f)
            f.write('\n')


def files_check(folder_paths):
    for folder_path in folder_paths:
        paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]
        print(f'{len(paths)} files found in: {folder_path}')
    print()


if __name__ == '__main__':
    main()

