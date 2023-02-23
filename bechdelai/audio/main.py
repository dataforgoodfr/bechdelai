import dependencies as dep
import audio_processor as ap

gender_segmentor = dep.get_gender_segmentor()
dialogue_tagger = dep.get_dialogue_tagger()
stt_transcriber = dep.get_gender_transcriber()


if __name__ == "__main__":
    AP = ap.AudioProcessor(".\\..\\..\\..\\HP4_extract2.wav", language="fr-FR")
    AP.export_to_csv("./HP4_results.csv")
    # AP.compute_speaking_time_allocation()
    # AP.compute_bechdel_scene_duration()
