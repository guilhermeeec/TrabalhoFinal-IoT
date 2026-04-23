from rtlsdr import RtlSdr

# Initialize the device
sdr = RtlSdr()

# Configure device parameters
sdr.sample_rate = 2.048e6  # Hz
sdr.center_freq = 102.1e6    # 102.1 MHz (adjust to a known local FM station)
sdr.gain = 'auto'

# Read 512 samples
samples = sdr.read_samples(512)

# Print the first 10 samples to verify data flow
print(f"Read {len(samples)} samples successfully.")
print(samples[:10])

# Clean up
sdr.close()
