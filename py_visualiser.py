import open3d as o3d
import numpy as np
import os 


# Get the directory where this script (py_visualiser.py) is physically located
script_dir = os.path.dirname(os.path.abspath(__file__))


# This ensures the script works regardless of where you run it from in the terminal
cloud_path = os.path.join(script_dir, "..", "epscan6.ply")

# Debug print to verify the path being checked
print(f"DEBUG: Looking for file at:\n{os.path.abspath(cloud_path)}")

# --- 2. LOADING ---
# Load the point cloud from the resolved path
pcd = o3d.io.read_point_cloud(cloud_path)

# Check if the point cloud contains any points
if not pcd.has_points():
    print("ERROR: File not found or is empty!")
    print("Please check if 'epscan6.ply' exists in the parent directory.")
else:
    print(f"Success! Loaded: {len(pcd.points)} points.")

    # --- NORMAL ESTIMATION ---
    # Calculating normals using PCA (Principal Component Analysis)
    normal_radius = 0.3 
    print(f"Estimating normals with radius {normal_radius}...")
    
    # Define search parameters for the KDTree (hybrid search: radius and max neighbors)
    search_param = o3d.geometry.KDTreeSearchParamHybrid(radius=normal_radius, max_nn=30)
    pcd.estimate_normals(search_param=search_param)
    
    # Orient normals consistently using tangent planes
    # This helps aligning normals so they point in a consistent direction (outwards)
    pcd.orient_normals_consistent_tangent_plane(k=15)

    print("Normal estimation completed.")

    # --- NORMAL FLIPPING ---
    # Invert the normals (multiply by -1) before building the mesh.
    # This is often necessary if the reconstructed mesh appears "inside out" (black faces).
    print("Flipping point cloud normals...")
    pcd.normals = o3d.utility.Vector3dVector(np.asarray(pcd.normals) * -1)

    # --- MESH RECONSTRUCTION (Ball Pivoting Algorithm) ---
    # Define radii for the virtual "balls" used in the BPA algorithm.
    # Different radii capture details at different scales.
    ball_radii = [0.009, 0.05, 0.1] 
    print(f"Using ball radii: {ball_radii}")
    
    # Create a triangle mesh from the point cloud using BPA
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
        pcd, 
        o3d.utility.DoubleVector(ball_radii) 
    )
    print("Ball Pivoting reconstruction completed.")

    # Transfer colors from the point cloud to the mesh vertices if available
    if pcd.has_colors():
        mesh.vertex_colors = pcd.colors

    # --- VISUALIZATION ---
    print("Displaying: BPA Mesh and Point Cloud")
    
    # Visualize the original point cloud
    o3d.visualization.draw_geometries([pcd], window_name="Point Cloud")
    
    # Visualize the reconstructed mesh
    o3d.visualization.draw_geometries([mesh], window_name="BPA Mesh")