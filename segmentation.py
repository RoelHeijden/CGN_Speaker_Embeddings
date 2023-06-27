

class Segmentation:

    def __init__(self, sr=8000):
        self.sr = sr

    def segment_dataset(self, dataset, labels):
        segments_dataset = []
        for waveform, (turns, speakers) in zip(dataset, labels):
            segments = self.segment_waveform(waveform, turns, speakers)
            segments_dataset.append(segments)
        return segments_dataset

    def segment_waveform(self, waveform, turns, speakers):
        segments = []

        # set custom speaker ID / index
        s1 = 0
        s2 = 1

        # at all times, these will point to the first next speaker turns for each speaker
        pointers = [0, 0]

        # get speaker of the first speaker turn
        if turns[s1][pointers[s1]][0] < turns[s2][pointers[s2]][0]:
            s = s1
        else:
            s = s2

        pointers[s] += 1

        # initialize first segment attributes
        segment_start, segment_end = turns[s][0]
        segment_speaker = speakers[s]
        segment_overlap = False

        # continue until both pointers reach the end of the list
        while pointers[s1] < len(turns[s1]) or pointers[s2] < len(turns[s2]):

            # check if both pointers haven't reached the end of the list yet
            if pointers[s1] < len(turns[s1]) and pointers[s2] < len(turns[s2]):
                # get the next first of the two speakers
                s = s2 if turns[s2][pointers[s2]][0] < turns[s1][pointers[s1]][0] else s1
            else:
                # if pointer 1 has reached the last turns list, we set s2 as speaker and vice versa
                if pointers[s1] >= len(turns[s1]):
                    s = s2
                if pointers[s2] >= len(turns[s2]):
                    s = s1

            # get speaker turn and increment pointer
            turn = turns[s][pointers[s]]
            pointers[s] += 1

            # variables to correctly set the speaker and time after a cutoff
            other_speaker_continues = False
            same_speaker_continues = False
            neither_speaker_continues = False
            prev_segment_end = segment_end

            # check if speaker turn overlaps with current segment
            has_overlap = segment_end > turn[0]
            if has_overlap:

                # calculate overlap time
                overlap_end = min(segment_end, turn[1])
                overlap = (turn[0], overlap_end)

                # check which speaker continues talking after this segment is cut off
                if segment_end < turn[1]:
                    other_speaker_continues = True
                elif segment_end > turn[1]:
                    same_speaker_continues = True
                elif segment_end == turn[1]:
                    neither_speaker_continues = True
                    pass

                # update segment attributes
                segment_end = min(segment_end, overlap_end)
                segment_overlap = overlap

            # create wav segment
            wav_segment = waveform[int(segment_start * self.sr):int(segment_end * self.sr)]

            # append segment
            segment = {
                'wav': wav_segment,
                'time': (segment_start, segment_end),
                'speaker': segment_speaker,
                'overlap': segment_overlap,
            }
            segments.append(segment)

            # correctly adjust segment attributes to continue at the end of the overlap
            if has_overlap:

                # check how the overlap has ended
                if same_speaker_continues:
                    segment_start = segment_end
                    segment_end = prev_segment_end

                elif other_speaker_continues:
                    segment_start = segment_end
                    segment_end = turn[1]

                    segment_speaker = speakers[0] if segment_speaker == speakers[1] else speakers[1]

                elif neither_speaker_continues:

                    # check if either pointer hasn't reached the end yet
                    if pointers[s1] >= len(turns[s1]) and pointers[s2] >= len(turns[s2]):
                        continue

                    # check if both pointers haven't reached the end of the list yet
                    if pointers[s1] < len(turns[s1]) and pointers[s2] < len(turns[s2]):
                        # get the next first of the two speakers
                        s = s2 if turns[s2][pointers[s2]][0] < turns[s1][pointers[s1]][0] else s1
                    else:
                        # if pointer 1 has reached the last turns list, we set s2 as speaker and vice versa
                        if pointers[s1] >= len(turns[s1]):
                            s = s2
                        if pointers[s2] >= len(turns[s2]):
                            s = s1

                    # get speaker turn and increment pointer
                    turn = turns[s][pointers[s]]
                    pointers[s] += 1

                    segment_start, segment_end = turn
                    segment_speaker = speakers[s]

            # correctly set segment attributes to continue with the new segment
            else:
                segment_speaker = speakers[s]
                segment_start, segment_end = turn

            segment_overlap = False

        return segments
















