const { SlashCommandBuilder } = require('discord.js')
const { joinVoiceChannel, createAudioPlayer, createAudioResource, AudioPlayerStatus, entersState, VoiceConnectionStatus } = require('@discordjs/voice');
const fs = require('node:fs')

module.exports = {
    data: new SlashCommandBuilder()
        .setName('join')
        .setDescription('Join a voice channel'),
    async execute(interaction) {
        if (interaction) {
            const connection = joinVoiceChannel({
                channelId: interaction.member.voice.channel.id,
                guildId: interaction.guild.id,
                adapterCreator: interaction.guild.voiceAdapterCreator
            });

            try {
                await entersState(connection, VoiceConnectionStatus.Ready, 10000);
                interaction.reply("Joined " + interaction.member.voice.channel.name);
            } catch (error) {
                console.error(error);
                connection.destroy();
                return;
            }

            // const player = createAudioPlayer();
            // connection.subscribe(player)

            // const resource = createAudioResource(fs.createReadStream('./speech-to-text/bocchi.mp3'))
            // player.play(resource)

            // await new Promise(resolve => {
            //     player.on(AudioPlayerStatus.Idle, () => {
            //         resolve();
            //     });
            // });
        } else {
            interaction.reply('You need to join a voice channel first!');
        }
    },
}