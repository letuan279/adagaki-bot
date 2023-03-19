const { SlashCommandBuilder } = require('@discordjs/builders');
const { getVoiceConnection, EndBehaviorType, joinVoiceChannel, entersState, VoiceConnectionStatus, createAudioPlayer, createAudioResource } = require('@discordjs/voice');
const { spawn } = require('child_process')
const ffmpeg = require('ffmpeg')
const fs = require('fs')

module.exports = {
    data: new SlashCommandBuilder()
        .setName('talk')
        .setDescription('Talking with you')
        .addStringOption(option => option.setName('question').setDescription('Your question').setRequired(true)),
    async execute(interaction) {
        let connection = getVoiceConnection(interaction.guild.id);

        if (!connection) {
            connection = joinVoiceChannel({
                channelId: interaction.member.voice.channel.id,
                guildId: interaction.guild.id,
                adapterCreator: interaction.guild.voiceAdapterCreator,
                selfDeaf: false,
                selfMute: false,
            });

            try {
                await entersState(connection, VoiceConnectionStatus.Ready, 10000);
                interaction.reply("Joined " + interaction.member.voice.channel.name);
            } catch (error) {
                console.error(error);
                connection.destroy();
                return;
            }
        }

        const question = interaction.options.getString('question')

        const utf8Text = Buffer.from(question, 'utf-8').toString('base64');

        const pythonProcess = spawn('python', ['./voice/c.py', utf8Text]);

        pythonProcess.stdout.on('data', (data) => {
            console.log(`stdout: ${data}`);
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`stderr: ${data}`);
        });

        pythonProcess.on('close', (code) => {
            const player = createAudioPlayer();
            connection.subscribe(player)

            const resource = createAudioResource(fs.createReadStream('./voice/voice.wav'))
            player.play(resource)
        });
    },
};
