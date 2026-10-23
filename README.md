# web-slide

面向科研组会、学术汇报与答辩的 HTML 幻灯片模板，包含配套 AI 排版 skill。使用浏览器即可离线查看、放映和编辑文字。

| 模板 | 学校 | 主题 | 使用说明 |
| --- | --- | --- | --- |
| [web-slide-ustb](web-slide-ustb/) | 北京科技大学 | 科技蓝、钢铁红 | [独立 README](web-slide-ustb/README.md) |
| [web-slide-lntu](web-slide-lntu/) | 辽宁工程技术大学 | 钢魂红、暖色浅底 | [独立 README](web-slide-lntu/README.md) |

每套提供 20 页版式示例：封面、字号与配色规范、目录、章节过渡、研究现状时间轴、公式、伪代码、实验比较表、图片、总结计划、参考文献、作者简介及尾页。实际汇报按内容选择版式，不必保留全部示例。

## 快速开始

1. 在 GitHub 点击 **Code → Download ZIP** 并解压，或 `git clone` 本仓库。
2. 进入所需学校的子目录，用 Chrome 或 Edge 打开 `template.html`。
3. 先复制模板再修改。工具栏支持文字编辑、加粗、主题色、排版检查和“保存HTML”。网页修改后需保存下载，才会保留。
4. 分享成品时，可发送“保存HTML”生成的独立文件；源模板分享时应保留完整子目录。

## 浏览与放映

- 单列滚动、多页预览（每行 1–6 页）、单页展示和全屏放映。
- 放映中使用方向键、PageUp / PageDown 或滚轮翻页；双击进入每行 4 页预览，再双击缩略页跳转。
- Ctrl + 滚轮按鼠标位置放大至 400%；放大后按住左键拖动。第一次 Esc 恢复原始大小，再按 Esc 退出。原生全屏的 Esc 行为可能受浏览器键盘锁支持影响。
- 选中文字可切换加粗或主题颜色；“恢复原色”恢复原位置的颜色。

## 交给 AI 制作与安装 skill

无需安装：让能访问本地文件的 AI 读取对应目录中的 `SKILL.md`，以同目录的 `template.html` 和资源制作新的汇报。

Windows 可进入学校子目录双击 **安装Skill.cmd**。安装器会读取 `CODEX_HOME`，否则使用 `~/.codex/skills/`，且拒绝覆盖已有技能。

| 模板目录 | 安装后的技能名 | 对话中调用 |
| --- | --- | --- |
| web-slide-ustb | beike-ppt-template | `$beike-ppt-template` |
| web-slide-lntu | lntu-ppt-template | `$lntu-ppt-template` |

其他系统可手动复制整个学校子目录到上表对应的技能目录，入口保留为 `SKILL.md`。安装后在下一轮对话调用，提供真实材料、用途和输出位置。

示例指令：

> 请读取所选模板的 SKILL.md，根据我提供的材料制作科研汇报，另存为新 HTML。按内容选择版式，检查换行、遮挡、边界、来源链接和页码，并导出 16:9 PDF。

## 环境与 PDF

| 操作 | 环境 |
| --- | --- |
| 查看、放映、编辑与保存 HTML | 推荐 Chrome / Edge，无需 Office、Python 或 Node.js |
| 精确导出 PDF、刷新图片缓存 | Python 3.10+；PDF 另需本地 Chrome / Edge；无第三方 Python 包 |
| 重绘数学公式 | 另需 XeLaTeX、dvisvgm、Cambria Math 及相关 TeX 宏包；日常使用不需要 |

Windows 双击学校子目录中的 `导出PDF.cmd`。也可在该子目录运行：

```powershell
python scripts/export-pdf.py
python scripts/export-pdf.py "我的汇报.html" --output "我的汇报.pdf"
```

页面画布为 1600×900 px，PDF 纸张为 960×540 pt，均为 16:9。导出工具校验页数与尺寸，避免 A4 白边及浏览器页眉页脚。浏览器编辑后先保存 HTML，再导出。附带 PDF 是预览快照。

## 维护与打包

在学校子目录运行 `python scripts/embed-assets.py` 更新图片缓存。修改公式后先运行 `python scripts/render-formulas.py`，再更新缓存。运行 `python scripts/package-template.py` 可生成该模板的独立 ZIP。

## 素材与使用说明

本项目是个人整理的科研汇报模板，并非学校官方产品。校名、校徽、校园照片及附带规范材料的权益属于各自权利人；辽工大选用素材及学校信息来源见其 `references/`。示例文字、参考文献及图片用于展示版式，制作正式报告时请核实并替换为真实内容。

当前未为整个仓库声明统一开源许可，公开可见不等于第三方素材获重新授权。两套模板均为 HTML 幻灯片与 skill 资源包，不是浏览器插件，也不是 PPTX 文件。
