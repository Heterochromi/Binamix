from binamix.sadie_utilities import *


# Set up your parameters.
subject_id = 'H7'               # Subject ID (D1, D2, H3 ... H20)
ir_type = 'HRIR'                # IR type (HRIR, BRIR)
azimuth = 95
elevation = 10
speaker_layout = '7.1.2'         # Speaker layout (5.1, 7.1, 5.1.4, 7.1.4, none)

# Gets the available angles for the given subject, sample rate, IR type, and speaker layout.
available_angles = get_available_angles(subject_id, 44100, ir_type, speaker_layout)

# Gets the nearest available angles to the given azimuth and elevation using Delaunay triangulation.
triangulation = delaunay_triangulation(available_angles, azimuth, elevation, speaker_layout, plots=True)

print(triangulation)  # Output: Delaunay triangulation object.
