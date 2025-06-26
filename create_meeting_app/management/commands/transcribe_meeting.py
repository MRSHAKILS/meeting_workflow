from django.core.management.base import BaseCommand
from create_meeting_app.models import Meeting, Transcript
import os
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage

GCS_BUCKET = os.getenv('GCS_BUCKET_NAME')
KEY_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
PROJECT_ID = os.getenv('GCP_PROJECT_ID')

speech_client = speech.SpeechClient.from_service_account_file(KEY_PATH)
storage_client = storage.Client.from_service_account_json(KEY_PATH)

class Command(BaseCommand):
    help = "Transcribe WAV files with speaker diarization using Google Speech-to-Text v1p1beta1"

    def add_arguments(self, parser):
        parser.add_argument('meeting_id', type=int)

    def handle(self, *args, **options):
        meeting_id = options['meeting_id']

        try:
            meeting = Meeting.objects.get(id=meeting_id)
        except Meeting.DoesNotExist:
            self.stderr.write("❌ Meeting not found.")
            return

        recordings = sorted([
            f for f in os.listdir("media/recordings")
            if f.endswith(".wav") and f"_{meeting_id}_" in f
        ])

        if not recordings:
            self.stdout.write("📭 No recordings found.")
            return

        for wav_file in recordings:
            path = os.path.join("media/recordings", wav_file)
            gcs_uri = f"gs://{GCS_BUCKET}/{wav_file}"
            self.stdout.write(f"🗣 Transcribing {wav_file} with diarization…")

            try:
                # Upload to GCS
                bucket = storage_client.bucket(GCS_BUCKET)
                blob = bucket.blob(wav_file)
                blob.upload_from_filename(path)
                self.stdout.write(f"☁️ Uploaded to {gcs_uri}")

                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code="en-US",
                    enable_speaker_diarization=True,
                    diarization_speaker_count=2,
                    model="video"  # video model = better for convo
                )

                audio = speech.RecognitionAudio(uri=gcs_uri)

                operation = speech_client.long_running_recognize(config=config, audio=audio)
                response = operation.result(timeout=600)

                # Process speaker segments
                speaker_transcripts = []
                for result in response.results:
                    alt = result.alternatives[0]
                    words = alt.words

                    current_speaker = None
                    current_text = []

                    for word in words:
                        if word.speaker_tag != current_speaker:
                            if current_text:
                                speaker_transcripts.append({
                                    "speaker": f"Speaker {current_speaker}",
                                    "text": " ".join(current_text)
                                })
                            current_speaker = word.speaker_tag
                            current_text = [word.word]
                        else:
                            current_text.append(word.word)

                    if current_text:
                        speaker_transcripts.append({
                            "speaker": f"Speaker {current_speaker}",
                            "text": " ".join(current_text)
                        })

                # 🔥 Nicely formatted transcript text:
                full_text = ""
                for segment in speaker_transcripts:
                    full_text += f"{segment['speaker'].upper()}:\n"
                    full_text += f"    {segment['text']}\n\n"

                Transcript.objects.create(meeting=meeting, text=full_text.strip())


                Transcript.objects.create(meeting=meeting, text=full_text.strip())

                os.remove(path)
                blob.delete()

                self.stdout.write("✅ Done and cleaned up")

            except Exception as e:
                self.stderr.write(f"⚠️ Error: {e}")
