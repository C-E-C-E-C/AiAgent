from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth


class Exporter:
    def export_pdf(self,content,filename = "travel_plan_pdf"):
        # 新建 PDF 画布，后面所有文字都写到这张 A4 页面上。
        c = canvas.Canvas(filename, pagesize=A4)
        page_width, page_height = A4
        left_margin = 50
        top_margin = 60
        bottom_margin = 50
        line_height = 18
        max_width = page_width - left_margin * 2

        def wrap_text(text):
            # 把长文本按页面宽度切成多行，避免 PDF 里一行太长被截断。
            lines = []
            for paragraph in str(text).splitlines():
                if not paragraph.strip():
                    lines.append("")
                    continue

                current_line = ""
                for char in paragraph:
                    candidate = current_line + char
                    if stringWidth(candidate, "Helvetica", 10) <= max_width:
                        current_line = candidate
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = char
                if current_line:
                    lines.append(current_line)
            return lines

        # 从页面顶部开始写标题和正文。
        y = page_height - top_margin
        c.setFont("Helvetica", 12)
        c.drawString(left_margin, y, "智能旅行助手行程")
        y -= line_height * 2
        c.setFont("Helvetica", 10)

        for line in wrap_text(content):
            if y < bottom_margin:
                # 当前页写满了就自动翻页，继续写下一页。
                c.showPage()
                c.setFont("Helvetica", 10)
                y = page_height - top_margin
            c.drawString(left_margin, y, line)
            y -= line_height

        c.save()
        # 保存后提示导出成功。
        print(f"PNDF 导出成功，文件名：{filename}")