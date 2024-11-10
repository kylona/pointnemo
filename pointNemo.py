import csv
import sys
from geopy.distance import geodesic
import scipy
import numpy as np
import matplotlib.pyplot as plt



# Function to read the CSV and return a list of (lat, lon) tuples
def read_csv(filename):
    points = []
    with open(filename, mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            lon, lat = float(row[0]), float(row[1])  # Longitude first, then latitude
            points.append((lat, lon))
    return points


# Function to convert between lat lon and x y z coordinates
# 6378137 is radius of earth
def latlon_to_xyz(latlon_points, radius=6378137):
    xyz_points = []
    for latlon in latlon_points:
        phi = latlon[0] * np.pi / 180
        theta = latlon[1] * np.pi / 180
        x = np.cos(phi) * np.cos(theta) * radius
        y = np.cos(phi) * np.sin(theta) * radius
        z = np.sin(phi) * radius
        xyz_points.append((x, y, z))
    return xyz_points

# Function to convert between x y z and lat lon coordinates
# 6378137 is radius of earth
def xyz_to_latlon(xyz_points, radius=6378137):
    latlon_points = []
    for xyz in xyz_points:
        x = xyz[0]
        y = xyz[1]
        z = xyz[2]
        XsqPlusYsq = x**2 + y**2
        phi = np.arctan2(z,np.sqrt(XsqPlusYsq))
        theta = np.arctan2(y,x)
        lat = phi * 180 / np.pi
        lon = theta * 180 / np.pi
        latlon_points.append((lat, lon))
    return latlon_points

def rotate_latlon_points(latlon_points, lat_r=90.0, lon_r=180.0):
    rotated_points = []
    for latlon in latlon_points:
        lat = latlon[0]
        lon = latlon[1]
        new_lat = (lat+90.0+lat_r) % 180.0 - 90.0
        new_lon = (lon+180.0+lon_r) % 360.0 - 180.0
        rotated_points.append((new_lat, new_lon))
    return rotated_points


# Given a set of x y z coordinates that fit on a sphere create a 3d spherical voronoi diagram 
# The edges of the diagram are where the closest point changes. 
# A most remote point will be one of the vertices of this diagram 
def get_spherical_voronoi_points(latlon_points, radius=6378137):
    # Convert to cartesian coordinates
    xyz_points = np.array(latlon_to_xyz(latlon_points))
    points = np.array(xyz_points)
    sv = scipy.spatial.SphericalVoronoi(points, radius)
    # Get the verticies of the voronoi diagram as candidates for the most remote point
    candidate_points = xyz_to_latlon(sv.vertices)

    rotated_points = rotate_latlon_points(latlon_points, lat_r=45.0, lon_r=90.0)
    xyz_points = np.array(latlon_to_xyz(rotated_points))
    points = np.array(xyz_points)
    sv = scipy.spatial.SphericalVoronoi(points, radius)
    # Get the verticies of the voronoi diagram as candidates for the most remote point
    rotated_candidate_points = xyz_to_latlon(sv.vertices)
    alt_candidate_points = rotate_latlon_points(rotated_candidate_points, lat_r=-45.0, lon_r=-90.0)
    combined_candidate_points = list(set(candidate_points).union(set(alt_candidate_points)))
    return combined_candidate_points

# Given a set of candidate points find the point that is furthest from any of the target points
def find_most_remote_point(candidate_points, target_points):
    distances = {}

    best_dist = 0 
    for i, (lat1, lon1) in enumerate(candidate_points):
        distances[i] = np.inf
        for (lat2, lon2) in target_points:
            dist = geodesic((lat1, lon1), (lat2, lon2)).kilometers
            if dist < distances[i]:
                distances[i] = dist
            if distances[i] < best_dist:
                break # No need to keep searching this won't be furthest
        if distances[i] > best_dist:
            best_dist = distances[i]

    max_key = max(distances, key=lambda i: distances[i])
    return candidate_points[max_key], distances[max_key]

def visualize_points(target_points, candidate_points, most_remote_latlon):
    xyz_target_points = np.array(latlon_to_xyz(target_points))
    xyz_candidate_points = np.array(latlon_to_xyz(candidate_points))
    result_point = latlon_to_xyz([most_remote_latlon])[0]
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(xyz_candidate_points[:, 0], xyz_candidate_points[:, 1], xyz_candidate_points[:, 2], c='g')
    ax.scatter(xyz_target_points[:, 0], xyz_target_points[:, 1], xyz_target_points[:, 2], c='b')
    ax.azim = 10 # rotate view
    ax.elev = 40
    _ = ax.set_xticks([])
    _ = ax.set_yticks([])
    _ = ax.set_zticks([])
    fig.set_size_inches(4, 4)
    ax.scatter([result_point[0]],[result_point[1]],[result_point[2]], c='r')
    plt.show()

def main():
    # Check if a filename was provided as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python compute_distances.py <filename1> [<filename2> . . .]")
        sys.exit(1)

    # The first command-line argument is the filename
    all_points = []
    for filename in sys.argv[1:]:
        # Read points from the CSV file
        points = read_csv(filename)
        all_points += points
    
    # Compute voronoi diagram
    candidate_points = get_spherical_voronoi_points(all_points)
    # Find the point that for all candidate points c and target points t argmax(min(dist(c, t)))
    most_remote_point, distance = find_most_remote_point(candidate_points, all_points)
    
    print(f"The most remote point is at {most_remote_point} that is {distance} kilometers away from the nearest point")
    visualize_points(all_points, candidate_points, most_remote_point)


if __name__ == '__main__':
    main()
