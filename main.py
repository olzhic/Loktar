import os
import telebot
from moviepy import AudioFileClip
import tempfile


class AudioBot:
    def __init__(self, token: str):
        self.bot = telebot.TeleBot(token)
        self._setup_handlers()

    def _setup_handlers(self):
        self.bot.message_handler(commands=['start'])(self.start_command)
        self.bot.message_handler(commands=['help'])(self.help_command)
        self.bot.message_handler(content_types=['audio', 'voice'])(self.handle_audio)

    def start_command(self, message):
        """Send a welcome message when the /start command is issued."""
        welcome_message = (
            "👋 Добро пожаловать в бота для обработки аудио!\n\n"
            "Отправьте мне любой аудиофайл или голосовое сообщение, и я могу:\n"
            "- Ускорить или замедлить его\n"
            "- Настроить громкость\n"
            "- Конвертировать между форматами\n\n"
            "Используйте /help для получения информации о доступных командах."
        )
        self.bot.reply_to(message, welcome_message)

    def help_command(self, message):
        """Send a help message when the /help command is issued."""
        help_message = (
            "🎵 Помощь по боту обработки аудио:\n\n"
            "Просто отправьте мне аудиофайл или голосовое сообщение.\n"
            "Добавьте эти подписи для разных эффектов:\n"
            "- 'speed:1.5' - Ускорить в 1.5 раза\n"
            "- 'speed:0.5' - Замедлить в 2 раза\n"
            "- 'convert:mp3' - Конвертировать в MP3\n"
            "- 'convert:wav' - Конвертировать в WAV"
        )
        self.bot.reply_to(message, help_message)

    def handle_audio(self, message):
        """Handle incoming audio files and voice messages."""
        try:
            processing_msg = self.bot.reply_to(message, "🎵 Обрабатываю ваше аудио...")


            if message.audio:
                file_info = self.bot.get_file(message.audio.file_id)
            else: 
                file_info = self.bot.get_file(message.voice.file_id)


            downloaded_file = self.bot.download_file(file_info.file_path)


            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_input:
                temp_input.write(downloaded_file)
                temp_input.flush()


                audio = AudioFileClip(temp_input.name)


                caption = message.caption.lower() if message.caption else ""
                processed_audio = self._process_audio(audio, caption)


                output_suffix = '.mp3'
                if caption and 'convert:wav' in caption:
                    output_suffix = '.wav'

                with tempfile.NamedTemporaryFile(delete=False, suffix=output_suffix) as temp_output:
                    processed_audio.write_audiofile(temp_output.name)
                    processed_audio.close()


                    with open(temp_output.name, 'rb') as audio_file:
                        self.bot.send_audio(
                            message.chat.id,
                            audio_file,
                            caption="✨ Вот ваше обработанное аудио!"
                        )


                    os.unlink(temp_output.name)

            os.unlink(temp_input.name)
            self.bot.delete_message(message.chat.id, processing_msg.message_id)

        except Exception as e:
            self.bot.reply_to(message, f"❌ Извините, произошла ошибка: {str(e)}")

    def _process_audio(self, audio: AudioFileClip, caption: str) -> AudioFileClip:
        """Process the audio according to the caption instructions."""
        if not caption:
            return audio


        if 'speed:' in caption:
            speed = float(caption.split('speed:')[1].split()[0])
            audio = audio.speedx(speed)

        return audio

    def run(self):
        """Run the bot."""
        print("Бот запущен...")
        self.bot.polling(none_stop=True)

if __name__ == "__main__":
    bot = AudioBot("7946249283:AAEnvin9qvyXaoICRPewub_wSdEiVmFH0fo")
    bot.run()
