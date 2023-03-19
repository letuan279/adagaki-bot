const { SlashCommandBuilder } = require('@discordjs/builders');
const { getVoiceConnection, EndBehaviorType, joinVoiceChannel, entersState, VoiceConnectionStatus, createAudioPlayer, createAudioResource } = require('@discordjs/voice');
const { createWriteStream } = require('node:fs');
const prism = require('prism-media');
const ffmpeg = require('ffmpeg')
const { pipeline } = require('node:stream');
const fs = require('fs')

module.exports = {
    data: new SlashCommandBuilder()
        .setName('listen')
        .setDescription('Start listening to the user in the voice channel.'),
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

        fs.watch('./voice', (eventType, filename) => {
            if (eventType === 'change' && filename === 'voice.wav') {
                const player = createAudioPlayer();
                connection.subscribe(player)

                const resource = createAudioResource(fs.createReadStream('./voice/voice.wav'))
                player.play(resource)
            }
        })
    },
};

function createListeningStream(receiver, userId, user) {
    const opusStream = receiver.subscribe(userId, {
        end: {
            behavior: EndBehaviorType.AfterSilence,
            duration: 2500,
        },
    });

    const oggStream = new prism.opus.OggLogicalBitstream({
        opusHead: new prism.opus.OpusHead({
            channelCount: 2,
            sampleRate: 48000,
        }),
        pageSizeControl: {
            maxPackets: 10,
        },
        crc: false
    });

    const filename = `./recordings/${user.id}.pcm`;

    const out = createWriteStream(filename, { flags: 'a' });
    console.log(`👂 Started recording ${filename}`);

    pipeline(opusStream, oggStream, out, (err) => {
        if (err) {
            console.warn(`❌ Error recording file ${filename} - ${err.message}`);
        } else {
            console.log(`✅ Recorded ${filename}`);
        }
    });
}
