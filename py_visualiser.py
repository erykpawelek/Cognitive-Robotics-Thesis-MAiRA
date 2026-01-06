import open3d as o3d
import numpy as np  


cloud = "epscan6.ply"

#Loading point cloud
pcd = o3d.io.read_point_cloud(cloud)

if not pcd.has_points():
    print("Błąd: Nie udało się wczytać chmury punktów.")
else:
    print(f"Praca na pełnej chmurze: {len(pcd.points)} punktów.")

    # OBLICZANIE NORMALNYCH PCA (Principal component analysis)
    promien_normalnych = 0.3 
    print(f"Obliczanie normalnych przy promieniu {promien_normalnych}...")
    search_param = o3d.geometry.KDTreeSearchParamHybrid(radius=promien_normalnych, max_nn=30)
    pcd.estimate_normals(search_param=search_param)
    
    # Próba orientacji (ale obraca źle)
    pcd.orient_normals_consistent_tangent_plane(k=15)

    print("Obliczanie normalnych zakończone.")

    # Odwracamy normalne na chmurze 'pcd' (mnożąc je przez -1)
    # Zanim jeszcze zbudujemy siatkę.
    print("Odwracanie normalnych chmury punktów...")
    pcd.normals = o3d.utility.Vector3dVector(np.asarray(pcd.normals) * -1)
   # REKONSTRUKCJA SIATKI (Ball Pivoting)
    promienie_kul = [0.009, 0.05, 0.1] 
    print(f"Używanie promieni kulek: {promienie_kul}")
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
        pcd, 
        o3d.utility.DoubleVector(promienie_kul) 
    )
    print("Rekonstrukcja Ball Pivoting zakończona.")
    # Przenosimy kolory
    if pcd.has_colors():
        mesh.vertex_colors = pcd.colors
    # 3. Wizualizacja
    print("Wyświetlanie: Siatka BPA (po lewej), Chmura punktów (po prawej)")

    #przesuniecie_x = pcd.get_max_bound()[0] - pcd.get_min_bound()[0]
    #pcd_copy = o3d.geometry.PointCloud(pcd) 
    #pcd_copy.translate((przesuniecie_x * 1.2, 0, 0)) 

    o3d.visualization.draw_geometries([pcd], window_name="Chmura punktów")
    o3d.visualization.draw_geometries([mesh], window_name="Siatka BPA")