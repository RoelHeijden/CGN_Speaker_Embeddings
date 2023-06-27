import librosa
import os
from tqdm import tqdm
import gzip


class DataProcessing:
    def __init__(self, max_n_files=-1, sr=8000):
        self.max_n_files = max_n_files
        self.sr = sr

    def load_dataset(self, folder_path):
        print('loading dataset')
        paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]
        print(f'{len(paths)} files found')

        if self.max_n_files >= 0:
            print(f"only loading {self.max_n_files}/{len(paths)} files")

        dataset = []
        for i, path in enumerate(tqdm(paths)):

            # break if set maximum amount of files is reached
            if i == self.max_n_files:
                break

            waveform, sample_rate = librosa.load(path, sr=None)  # sampling rate is 8000
            dataset.append(waveform)

            # double check sample rate
            if self.sr != sample_rate:
                print(f"WARNING: sampling rate of {sample_rate} does not match {self.sr}")

        return dataset

    def load_speaker_labels(self, folder_path):
        paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]

        # these are characters the file uses to indicate certain attributes
        file_start_char = '"IntervalTier"'
        no_audio_char = '""'
        speakers_to_ignore = ["BACKGROUND", "COMMENT", "UNKNOWN"]

        all_turns = []
        for j, path in enumerate(paths):

            # break if set maximum amount of files is reached
            if j == self.max_n_files:
                break

            # open the file
            with gzip.open(path, 'rt') as f:
                lines = f.readlines()

                # keep track of turns for both speakers
                turns = ([], [])

                # keep track of the current speaker
                speaker = None
                speakers = []

                # keep track whether new lines are happening mid sentence
                mid_sentence = False

                # read each line of the file
                for i, line in enumerate(lines):
                    line = line.strip('\n')

                    # check for speakerID if file start
                    if line == file_start_char:

                        # check if previous speaker wasn't mid-sentence when file cut off. If so: add datapoint
                        if mid_sentence:
                            turns[speakers.index(speaker)].append((start_time, end_time))
                            mid_sentence = False

                        # set new speaker
                        speaker = lines[i + 1].strip('\n"')

                        if speaker not in speakers_to_ignore:
                            speakers.append(speaker)
                        continue

                    # skip if the audio source is not one of the two speakers
                    if speaker in speakers_to_ignore:
                        continue

                    # check if the content of the file has started. it starts after the first speakerID
                    if not speaker or line.strip('"') == speaker:
                        continue

                    # check if line contains sentence
                    if line.startswith('"') and line.endswith('"') and not line == no_audio_char:
                        end_time = float(lines[i - 1])
                        if not mid_sentence:
                            start_time = float(lines[i - 2])
                            mid_sentence = True

                    # check if end of speaker turn:
                    if line == no_audio_char:

                        # add datapoint if a speaker was previously mid-sentence
                        if mid_sentence:
                            turns[speakers.index(speaker)].append((start_time, end_time))
                            mid_sentence = False

            # add speaker turns to the final list
            all_turns.append((turns, speakers))

        return all_turns

    def preprocess_dataset(self, dataset):
        print('preprocessing dataset')
        for i, waveform in enumerate(tqdm(dataset)):
            dataset[i] = self.normalize_waveform(waveform)

        return dataset

    def normalize_waveform(self, waveform):
        max_amp = max(abs(waveform))
        normalized_waveform = waveform / max_amp
        return normalized_waveform






