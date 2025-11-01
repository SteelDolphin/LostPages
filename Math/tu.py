import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

def plot_vector_field(P, Q, x_range=(-3, 3), y_range=(-3, 3), points=30,
                        title=None, density=1.0, scale=40, cmap=None, show=False):
    """
    绘制二维向量场并返回 matplotlib Figure 对象。
    参数:
        P, Q: 可以是可调用对象 f(X, Y) 返回 U, V（numpy 数组），
            或者直接传入与网格匹配的 ndarray。
        x_range, y_range: x/y 的取值区间 (min, max)。
        points: 网格每个方向的采样点数。
        title: 图像标题（字符串）。
        density: streamplot 的密度参数。
        scale: quiver 的 scale 参数。
        cmap: contourf 使用的颜色映射，默认为 plt 默认。
    返回:
        fig: matplotlib.figure.Figure
    """
    # 构造网格
    x = np.linspace(x_range[0], x_range[1], points)
    y = np.linspace(y_range[0], y_range[1], points)
    X, Y = np.meshgrid(x, y)

    # 计算 U, V：支持可调用或 ndarray
    if callable(P):
        U = P(X, Y)
    else:
        U = np.asarray(P)
        if U.shape != X.shape:
            raise ValueError("P 的形状必须与网格匹配或为可调用函数")

    if callable(Q):
        V = Q(X, Y)
    else:
        V = np.asarray(Q)
        if V.shape != X.shape:
            raise ValueError("Q 的形状必须与网格匹配或为可调用函数")

    # 计算幅值并绘图
    mag = np.sqrt(U**2 + V**2)

    fig = plt.figure(figsize=(8, 6))
    # 启用常见中文字体以避免中文乱码，禁用负号被替换为方块
    mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
    mpl.rcParams['axes.unicode_minus'] = False

    if cmap is None:
        cmap = plt.cm.viridis

    plt.contourf(X, Y, mag, levels=30, alpha=0.8, cmap=cmap)
    plt.colorbar(label="向量幅值 (magnitude)")
    plt.quiver(X, Y, U, V, pivot='mid', scale=scale)
    plt.streamplot(X, Y, U, V, density=density, color='orange')
    plt.title(title if title is not None else "二维向量场")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.axis('equal')
    plt.tight_layout()
    if show:
        plt.show()

    return fig

def visualize_curl_field(P_func, Q_func, x_range=(-3, 3), y_range=(-3, 3), points=30,
                            title=None, density=1.0, show=False):
    """
    可视化二维向量场的旋度分布。
    参数:
        P_func: 可调用对象 f(X, Y) 返回向量场的 x 分量（numpy 数组）。
        Q_func: 可调用对象 f(X, Y) 返回向量场的 y 分量（numpy 数组）。
        x_range, y_range: x/y 的取值区间 (min, max)。
        points: 网格每个方向的采样点数。
    """
    # 构造网格
    x = np.linspace(x_range[0], x_range[1], points)
    y = np.linspace(y_range[0], y_range[1], points)
    X, Y = np.meshgrid(x, y)

    P = P_func(X, Y)   # shape (ny, nx)
    Q = Q_func(X, Y)

    dQdy, dQdx = np.gradient(Q, y, x)   # returns [∂Q/∂y, ∂Q/∂x]
    dPdy, dPdx = np.gradient(P, y, x)
    # 计算旋度
    curl_z = dQdx - dPdy

    mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
    mpl.rcParams['axes.unicode_minus'] = False

    # 绘制旋度分布
    fig = plt.figure(figsize=(8, 6))
    plt.contourf(X, Y, curl_z, levels=30, cmap='coolwarm')
    plt.colorbar(label="旋度 (z 分量)")
    # 添加流线
    plt.streamplot(X, Y, P, Q, color='black', linewidth=1, density=density, arrowsize=1)
    plt.title("二维向量场的旋度可视化", fontsize=14)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.axis('equal')
    plt.tight_layout()
    if show:
        plt.show()

    return fig




# 若作为脚本直接运行，使用原示例作为演示
if __name__ == "__main__":
    # 示例向量场 F(x,y) = (-y + 0.5*x, x + 0.5*y)
    fig1 = plot_vector_field(lambda X, Y: -Y + 0.5 * X,
                        lambda X, Y:  X + 0.5 * Y,
                        title="示例二维向量场：F(x,y)=(-y+0.5x, x+0.5y)",
                        show=True)
    # # 示例向量场 F(x,y) = (-y, x)
    # plot_vector_field(lambda X, Y: -Y,
    #                     lambda X, Y:  X,
    #                     title="示例二维向量场：F(x,y)=(-y, x)")
    # 计算并可视化该向量场的旋度
    def P_func(X, Y):
        return -Y + 0.5 * X

    def Q_func(X, Y):
        return X + 0.5 * Y
    fig2 = visualize_curl_field(P_func, Q_func, show=True)
