import taichi as ti

# 初始化 Taichi
ti.init(arch=ti.gpu)

# 窗口分辨率
res_x, res_y = 800, 600
pixels = ti.Vector.field(3, dtype=ti.f32, shape=(res_x, res_y))

# 定义全局交互参数
Ka = ti.field(ti.f32, shape=())
Kd = ti.field(ti.f32, shape=())
Ks = ti.field(ti.f32, shape=())
shininess = ti.field(ti.f32, shape=())

@ti.func
def normalize(v):
    return v / v.norm(1e-5)

@ti.func
def reflect(I, N):
    return I - 2.0 * I.dot(N) * N

@ti.func
def intersect_sphere(ro, rd, center, radius):
    t = -1.0
    normal = ti.Vector([0.0, 0.0, 0.0])
    oc = ro - center
    b = 2.0 * oc.dot(rd)
    c = oc.dot(oc) - radius * radius
    delta = b * b - 4.0 * c
    if delta > 0:
        t1 = (-b - ti.sqrt(delta)) / 2.0
        if t1 > 0:
            t = t1
            p = ro + rd * t
            normal = normalize(p - center)
    return t, normal

@ti.func
def intersect_cone(ro, rd, apex, base_y, radius):
    t = -1.0
    normal = ti.Vector([0.0, 0.0, 0.0])
    H = apex.y - base_y
    k = (radius / H) ** 2
    ro_local = ro - apex
    A = rd.x**2 + rd.z**2 - k * rd.y**2
    B = 2.0 * (ro_local.x * rd.x + ro_local.z * rd.z - k * ro_local.y * rd.y)
    C = ro_local.x**2 + ro_local.z**2 - k * ro_local.y**2
    if ti.abs(A) > 1e-5:
        delta = B**2 - 4.0 * A * C
        if delta > 0:
            t1 = (-B - ti.sqrt(delta)) / (2.0 * A)
            t2 = (-B + ti.sqrt(delta)) / (2.0 * A)
            t_first = t1 if t1 < t2 else t2
            y1 = ro_local.y + t_first * rd.y
            if t_first > 0 and -H <= y1 <= 0:
                t = t_first
            else:
                t_second = t2 if t1 < t2 else t1
                y2 = ro_local.y + t_second * rd.y
                if t_second > 0 and -H <= y2 <= 0:
                    t = t_second
            if t > 0:
                p_local = ro_local + rd * t
                normal = normalize(ti.Vector([p_local.x, -k * p_local.y, p_local.z]))
    return t, normal

@ti.kernel
def render():
    for i, j in pixels:
        u = (i - res_x / 2.0) / res_y * 2.0
        v = (j - res_y / 2.0) / res_y * 2.0
        ro = ti.Vector([0.0, 0.0, 5.0])
        rd = normalize(ti.Vector([u, v, -1.0]))

        min_t = 1e10
        hit_normal = ti.Vector([0.0, 0.0, 0.0])
        hit_color = ti.Vector([0.0, 0.0, 0.0])
        
        # 场景物体
        sp_center = ti.Vector([-1.2, -0.2, 0.0])
        sp_rad = 1.2
        t_sph, n_sph = intersect_sphere(ro, rd, sp_center, sp_rad)
        if 0 < t_sph < min_t:
            min_t, hit_normal, hit_color = t_sph, n_sph, ti.Vector([0.8, 0.1, 0.1])
            
        cone_apex = ti.Vector([1.2, 1.2, 0.0])
        t_cone, n_cone = intersect_cone(ro, rd, cone_apex, -1.4, 1.2)
        if 0 < t_cone < min_t:
            min_t, hit_normal, hit_color = t_cone, n_cone, ti.Vector([0.6, 0.2, 0.8])

        color = ti.Vector([0.05, 0.15, 0.15])
        if min_t < 1e9:
            p = ro + rd * min_t
            N = hit_normal
            light_pos = ti.Vector([2.0, 3.0, 4.0])
            L = normalize(light_pos - p)
            V = normalize(ro - p)

            # 硬阴影检测
            shadow_ro = p + N * 1e-3
            t_s1, _ = intersect_sphere(shadow_ro, L, sp_center, sp_rad)
            t_s2, _ = intersect_cone(shadow_ro, L, cone_apex, -1.4, 1.2)
            dist_to_light = (light_pos - p).norm()
            in_shadow = (t_s1 > 0 and t_s1 < dist_to_light) or (t_s2 > 0 and t_s2 < dist_to_light)

            # Blinn-Phong 计算
            ambient = Ka[None] * hit_color
            diffuse = ti.Vector([0.0, 0.0, 0.0])
            specular = ti.Vector([0.0, 0.0, 0.0])
            
            if not in_shadow:
                diff = ti.max(0.0, N.dot(L))
                diffuse = Kd[None] * diff * hit_color
                
                H = normalize(L + V) # 半程向量
                spec = ti.pow(ti.max(0.0, N.dot(H)), shininess[None])
                specular = Ks[None] * spec * ti.Vector([1.0, 1.0, 1.0])
            
            color = ambient + diffuse + specular
        pixels[i, j] = ti.math.clamp(color, 0.0, 1.0)

def main():
    window = ti.ui.Window("Blinn-Phong & Shadows", (res_x, res_y))
    canvas = window.get_canvas()
    gui = window.get_gui()
    Ka[None], Kd[None], Ks[None], shininess[None] = 0.2, 0.7, 0.5, 32.0
    while window.running:
        render()
        canvas.set_image(pixels)
        with gui.sub_window("Material", 0.05, 0.05, 0.25, 0.25):
            Ka[None] = gui.slider_float('Ka', Ka[None], 0.0, 1.0)
            Kd[None] = gui.slider_float('Kd', Kd[None], 0.0, 1.0)
            Ks[None] = gui.slider_float('Ks', Ks[None], 0.0, 1.0)
            shininess[None] = gui.slider_float('Shininess', shininess[None], 1.0, 128.0)
        window.show()

if __name__ == '__main__':
    main()