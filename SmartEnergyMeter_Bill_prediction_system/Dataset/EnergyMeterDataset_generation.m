clc;
clear;

% ==============================
% CONFIG
% ==============================
num_days = 60;
start_date = datetime(2025,1,1,0,0,0);

N = num_days * 24;

timestamp = NaT(N,1);
hour_of_day = zeros(N,1);
power = zeros(N,1);
energy = zeros(N,1);

idx = 1;

% Bulb ratings
bulb1 = 60;
bulb2 = 60;

for d = 0:num_days-1
    for h = 0:23

        t = start_date + days(d) + hours(h);

        % ==============================
        % TIME-BASED USAGE PROBABILITY
        % ==============================
        if h >= 0 && h <= 5
            p_on = 0.3;
        elseif h >= 6 && h <= 9
            p_on = 0.6;
        elseif h >= 10 && h <= 16
            p_on = 0.5;
        elseif h >= 17 && h <= 21
            p_on = 0.9;
        else
            p_on = 0.6;
        end

        % ==============================
        % BULB STATES
        % ==============================
        bulb1_on = rand() < p_on;
        bulb2_on = rand() < (p_on - 0.1);

        load_power = bulb1*bulb1_on + bulb2*bulb2_on;

        % ==============================
        % BASE LOAD (IMPORTANT FIX)
        % ==============================
        base = 5 + rand()*10;   % 5–15W standby

        % ==============================
        % FINAL POWER
        % ==============================
        p = load_power + base + randn()*2;

        % Clamp
        p = max(p, 5);

        % Small spike
        if rand() < 0.03
            p = p + 10 + rand()*10;
        end

        % Energy
        e = p / 1000;

        % Store
        timestamp(idx) = t;
        hour_of_day(idx) = h;
        power(idx) = p;
        energy(idx) = e;

        idx = idx + 1;
    end
end

T = table(timestamp, hour_of_day, power, energy);

writetable(T, 'final_dataset.csv');

disp('✅ Dataset ready!');
disp(T(1:10,:));

figure;
plot(T.timestamp(1:48), T.power(1:48), '-o');
title('Sample Power (First 2 Days)');
xlabel('Time'); ylabel('Power (W)');
grid on;