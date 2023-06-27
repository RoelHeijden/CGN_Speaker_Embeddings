from pyannote.audio import Model
import torch
import numpy as np
from tqdm import tqdm


class Embedding:
    def __init__(self, sr=8000):
        self.sr = sr
        print("Create a Huggingface access token to access the Pyannote embedding model !")
        self.model = Model.from_pretrained("pyannote/embedding", use_auth_token="INSERT_YOUR_ACCESS_TOKEN_HERE").eval().to("cpu", dtype=float)

    def create_embeddings(self, dataset):
        print("creating speaker embeddings")

        # dict key constants
        SPEAKER1 = 'speaker1'
        SPEAKER2 = 'speaker2'
        OVERLAP = 'overlap'

        embedding_dataset = []
        for segments in tqdm(dataset):

            # init output format
            embeddings = {
                SPEAKER1: [],
                SPEAKER2: [],
                SPEAKER1 + OVERLAP: [],
                SPEAKER2 + OVERLAP: [],
            }

            # get unique speakers
            unique_speakers = []
            for segment in segments:
                s = segment['speaker']
                if s not in unique_speakers:
                    unique_speakers.append(s)
                if len(unique_speakers) >= 2:
                    break

            # speaker ID to speaker key mapping
            speaker_mapping = {
                unique_speakers[0]: SPEAKER1,
                unique_speakers[1]: SPEAKER2,
            }

            # iterate over each segment in the conversation
            for segment in segments:

                # load segment data
                wav = segment['wav']
                time = segment['time']
                speaker = segment['speaker']
                overlap = segment['overlap']

                # skip if audio segment is less than the minimum required for the embedding model
                if len(wav) < 5100:
                    continue

                # get embedding
                input_wav = torch.tensor(wav).unsqueeze(0)
                embedding = self.model(input_wav).squeeze(0).detach().tolist()

                # if segment contains no overlapping speech
                if not overlap:

                    # calculate total segment time
                    total_time = abs(time[0] - time[1])

                    # add datapoint
                    embeddings[speaker_mapping[speaker]].append(
                        {
                            'speaker': speaker,
                            'time': round(total_time, 3),
                            'embedding': embedding,
                         }
                    )

                # if the segment does contain overlapping speech
                else:
                    # calculate total segment time, total overlap and total speaker times
                    total_time = abs(time[0] - time[1])
                    total_overlap_time = abs(overlap[0] - overlap[1])

                    # calculate percentage of speech: e.g. 25% overlap, 40% s1, 35% s2
                    perc_overlap = total_overlap_time / total_time

                    # add datapoint
                    embeddings[speaker_mapping[speaker] + OVERLAP].append(
                        {
                            'speaker': speaker,
                            'time': round(total_time, 3),
                            'overlap%': round(perc_overlap, 3),
                            'embedding': embedding,
                         }
                    )

            # store data
            embedding_dataset.append(embeddings)

        return embedding_dataset

    def generate_random_embeddings(self, n_files, n_segments, segment_length=16000):
        print("creating random embeddings")

        embeddings = []
        for _ in tqdm(range(n_files)):
            file_embeddings = []

            for _ in range(n_segments):
                # Generating random noise waveform
                noise = np.random.uniform(-1.0, 1.0, segment_length)
                input_wav = torch.tensor(noise).unsqueeze(0)

                # Compute the embedding
                embedding = self.model(input_wav).squeeze(0).detach().tolist()

                file_embeddings.append(embedding)
            embeddings.append(file_embeddings)

        return embeddings



