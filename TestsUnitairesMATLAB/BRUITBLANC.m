close all; clear all; clc;

addpath(genpath('01-Echo-Hiding-Single-Kernel'));
addpath(genpath('02-Echo-Hiding-NP-Kernel'));
addpath(genpath('03-Echo-Hiding-BF-Kernel'));
addpath(genpath('04-Echo-Hiding-Mirrored-Kernel'));
addpath(genpath('05-Echo-Hiding-Time-Spread'));

audio = audioload();

text = 'Message Echo-Cache Plus long pour favoriser la precision des erreurs fvdghefhzigifzf54g1ze5g5z1eg32z1fg535z41v3ezr4vg1er64vgf1egr6z41rvg36zer41vg6r7z4r*6g41z6g451zg-hzr4g6';

out = echo_enc_single(audio.data, text, 128, 256, 0.5, 2048);
out2 = echo_enc_np(audio.data, text, 128, 256, 0.5, 2048);
out3 = echo_enc_bf(audio.data, text, 128, 256, 0.5, 2048);
out4 = echo_enc_mirror(audio.data, text, 128, 256, 0.5, 2048);
out5 = echo_enc_ts(audio.data, text, 128, 256, 0.04, 2048);

valm = max([max(out) min(out)*-1]);

output = zeros(1000, 1);
output2 = zeros(1000, 1);
output3 = zeros(1000, 1);
output4 = zeros(1000, 1);
output5 = zeros(1000, 1);
bruit = zeros(length(out), 1);

for i = 1:length(out)
     bruit(i) = (2*(rand - 0.5)*valm/1000);
end

for i = 1:1000
    msg = echo_dec(out + bruit * i, 2048, 128, 256);
    err = BER(text,msg);
    output(i) = err;
    
    msg = echo_dec(out2 + bruit * i, 2048, 128, 256);
    err = BER(text,msg);
    output2(i) = err;
    
    msg = echo_dec(out3 + bruit * i, 2048, 128, 256);
    err = BER(text,msg);
    output3(i) = err;
    
    msg = echo_dec(out4 + bruit * i, 2048, 128, 256);
    err = BER(text,msg);
    output4(i) = err;
    
    msg = echo_dec_ts(out5 + bruit * i, 2048, 128, 256);
    err = BER(text,msg);
    output5(i) = err;
end

figure;
hold on;
plot(0.1:0.1:100, output);
plot(0.1:0.1:100, output2);
plot(0.1:0.1:100, output3);
plot(0.1:0.1:100, output4);
plot(0.1:0.1:100, output5);
xlabel('Percent of added White Noise');
ylabel('Percent of Decode Errors');
legend({'Echo Single', 'Echo Bipolar', 'Echo BF', 'Echo BF Bipolar', 'Echo Time-Spread'}, 'location', 'southeast');
