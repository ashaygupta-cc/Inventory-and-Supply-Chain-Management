import re

def list_chapters(filename):
    try:
        content = open(filename, 'r', encoding='utf-8').read()
        chapters = re.findall(r'\\chapter\{(.*?)\}', content)
        return chapters
    except Exception as e:
        return str(e)

print("Project Report Chapters:", list_chapters('project_report.tex'))
print("WB Report Chapters:", list_chapters('white_box_testing.tex'))
