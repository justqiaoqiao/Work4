# Taichi Phong 局部光照渲染实验
## 项目简介
基于 Taichi 实现光线投射(Ray Casting) + Phong 光照交互式渲染，无外部模型，使用隐式方程生成球体、圆锥，UI滑块实时调节光照材质参数。

## 实验目标
1. 理解 Phong 三分量光照：Ambient 环境光 / Diffuse 漫反射 / Specular 镜面高光
2. 掌握三维向量运算、光线求交、Z-Buffer 深度遮挡逻辑
3. 使用 Taichi 完成光线渲染与交互式参数调节

## 光照原理
Phong 总光照公式：
$$I = I_{ambient} + I_{diffuse} + I_{specular}$$
- Ambient：全局均匀背景光
- Diffuse：朗伯漫反射，依赖法向量与光线夹角
- Specular：镜面高光，高光指数控制光斑范围

## 场景配置
- 物体：左侧红色球体、右侧紫色圆锥（隐式几何求交）
- 相机位置：(0, 0, 5)
- 白光点光源：(2, 3, 4)
- 深度测试：实现 Z-Buffer，取最近交点完成遮挡着色

## 可调交互参数
| 参数 | 调节范围 | 默认值 |
|------|----------|--------|
| Ka 环境光系数 | 0.0 ~ 1.0 | 0.2 |
| Kd 漫反射系数 | 0.0 ~ 1.0 | 0.7 |
| Ks 高光系数 | 0.0 ~ 1.0 | 0.5 |
| Shininess 高光指数 | 1.0 ~ 128.0 | 32.0 |

## 环境依赖
- Python 3.8+
- taichi >= 1.4.0

## 渲染演示效果
<p align="center">
  <img src="work4_images/work4_one.gif" width="720" alt="Ka环境光调节演示">
  <br><br>
  <img src="work4_images/work4_two.gif" width="720" alt="Kd漫反射调节演示">
  <br><br>
  <img src="work4_images/work4_three.gif" width="720" alt="Ks高光强度调节演示">
  <br><br>
  <img src="work4_images/work4_four.gif" width="720" alt="Shininess高光指数调节演示">
</p>

安装命令：
```bash
pip install taichi


