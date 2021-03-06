""" 
    This archive is for plotting the values of the achievable rate and outage probability.

"""

import numpy as np
import matplotlib.pyplot as plt
import uavnoma

# Variable simulation parameters
monte_carlo_samples = 100000  # Monte Carlo samples
power_los = 1.0 # power of Line-of-Sigth path & scattered paths (1<= power_los <= 2)
rician_factor = 15 # Rician factor value (10<= rician_factor <= 15)
path_loss = 2.2 # Path loss exponent (2 <= path_loss <= 3)
snr_dB = np.array(range(10, 61, 2)) # SNR in dB
snr_linear = 10.0 ** (snr_dB / 10.0)  # SNR linear
radius_uav = 2.0 # Radius fly trajectory of the UAV in meters
radius_user = 10.0  # Distribution radius of users in the cell in meters.
uav_heigth_mean = 15.0 # Average UAV flight height
target_rate_primary_user = 0.5 # Target rate bits/s/Hertz  primary user
target_rate_secondary_user = 0.5 # Target rate bits/s/Hertz  secondary user
hardw_ip = 0.0 # Residual Hardware Impairments
sic_ip = 0.0  # Residual Imperfect SIC


# fixed simulation parameters
number_user = 2 # Number of users
number_uav = 1 # Number of UAV

# Initialization of some auxiliary arrays
out_probability_system = np.zeros((monte_carlo_samples, len(snr_dB)))
out_probability_secondary_user = np.zeros((monte_carlo_samples, len(snr_dB)))
out_probability_primary_user = np.zeros((monte_carlo_samples, len(snr_dB)))
system_average_rate = np.zeros((monte_carlo_samples, len(snr_dB)))
rate_secondary_user = np.zeros((monte_carlo_samples, len(snr_dB)))
rate_primary_user = np.zeros((monte_carlo_samples, len(snr_dB)))


# ------------------------------------------------------------------------------------
# Fixed power allocation
power_coeff_primary = float(input('Enter the value of power coefficient allocation of the Primary User: ')) 
power_coeff_secondary = 1 - power_coeff_primary
assert (
    power_coeff_primary >= power_coeff_secondary
),  "The power coefficient of the primary user must be greater than that of the Secondary user."

sum_power = power_coeff_primary + power_coeff_secondary
assert (sum_power > 0) and (
    sum_power <= 1
) , "The sum of the powers must be > 0 or <= 1."

        
for mc in range(monte_carlo_samples):
    # Position UAV and users
    uav_axis_x, uav_axis_y, uav_heigth = uavnoma.random_position_uav(number_uav, radius_uav, uav_heigth_mean)
    user_axis_x, user_axis_y = uavnoma.random_position_users(number_user, radius_user)

    s, sigma = uavnoma.fading_rician(rician_factor, power_los)

    # Generate channel gains
    channel_gain_primary, channel_gain_secondary =  uavnoma.generate_channel(
        s,
        sigma,
        number_user,
        user_axis_x,
        user_axis_y,
        uav_axis_x,
        uav_axis_y,
        uav_heigth,
        path_loss,
    )

    # Analyzes system performance metrics for various SNR values
    for sn in range(0, len(snr_dB)):

        # Calculating achievable rate of primary user
        rate_primary_user[mc, sn] = uavnoma.calculate_instantaneous_rate_primary(
            channel_gain_primary,
            snr_linear[sn],
            power_coeff_primary,
            power_coeff_secondary,
            hardw_ip,
        )
        # Calculating achievable rate of secondary user
        rate_secondary_user[mc, sn] = uavnoma.calculate_instantaneous_rate_secondary(
            channel_gain_secondary,
            snr_linear[sn],
            power_coeff_secondary,
            power_coeff_primary,
            hardw_ip,
            sic_ip,
        )

        system_average_rate[mc, sn] = uavnoma.average_rate(rate_primary_user[mc, sn], rate_secondary_user[mc, sn])
        
        # Calculating of outage probability of the system
        out_probability_system[mc, sn], out_probability_primary_user[mc, sn], out_probability_secondary_user[mc, sn] = uavnoma.outage_probability(
            rate_primary_user[mc, sn],
            rate_secondary_user[mc, sn], 
            target_rate_primary_user,
            target_rate_secondary_user,
        )

# Outage Probability
out_prob_mean = np.mean(
    out_probability_system, axis=0
)  # Outage probability of the System
out_prob_primary = np.mean(
    out_probability_primary_user, axis=0
)  # Outage probability of the Primary User
out_prob_secondary = np.mean(
    out_probability_secondary_user, axis=0
)  # Outage probability of the Secondary User

# Achievable Rate
average_rate_mean = np.mean(
    system_average_rate, axis=0
)  # Average achievable rate of the system
rate_mean_primary_user = np.mean(
    rate_primary_user, axis=0
)  # Average achievable rate of the Primary User
rate_mean_secondary_user = np.mean(
    rate_secondary_user, axis=0
)  # Average achievable rate of the Secondary User


print("Outage probability system:", out_prob_mean)
print("Average Achievable Rate of the System:", average_rate_mean)
print("Achievable Rate of the Primary user:", rate_primary_user)
print("Achievable Rate of the Secondary user:", rate_secondary_user)


# Saving outage probability values in .txt
print('Outage probability system:', out_prob_mean, '\n\nOutage probability primary user:', out_prob_primary, '\n\nOutage probability secondary user:', out_prob_secondary, file=open("tutorial/data/outage_prob_values.txt", "w"))

# Saving achievable rate values in .txt
print(' Average Achievable Rate of the System:', average_rate_mean, '\n\nAverage achievable rate of the Primary User:', rate_mean_primary_user, '\n\nAverage achievable rate of the Secondary User:', rate_mean_secondary_user, file=open("tutorial/data/achievable_rate_values.txt", "w"))

# --------------------- FIGURES -----------------------------
plot = "yes" 
if plot == "yes":
    # Outage probability
   # plt.semilogy(snr_dB, out_prob_mean, "go-", label="System", linewidth=2)
    plt.semilogy(snr_dB, out_prob_primary, "b.-", label="Primary user", linewidth=1)
    plt.semilogy(snr_dB, out_prob_secondary, "r.-", label="Secondary user", linewidth=1)
    plt.xlabel("SNR (dB)")
    plt.ylabel("Outage Probability")
    plt.legend(loc="lower left")
    plt.xlim(10, 40)

    # Average Achievable Rate of the users
    plt.figure()
    plt.plot(snr_dB, rate_mean_primary_user, "b.-", label="primary user", linewidth=1)
    plt.plot(
        snr_dB, rate_mean_secondary_user, "r.-", label="secondary user", linewidth=1
    )
    plt.xlim(10, 60)
    plt.xlabel("SNR (dB)")
    plt.ylabel("Achievable rate (bits/s/Hz)")
    plt.legend(loc="upper left")

    plt.show()
    