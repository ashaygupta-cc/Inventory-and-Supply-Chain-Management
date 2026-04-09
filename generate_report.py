import re

def parse_tex_files():
    parts = {}
    
    tex_content = open('project_report.tex', 'r', encoding='utf-8').read()
    
    # Split by \chapter{
    chapter_blocks = tex_content.split('\\chapter{')
    for block in chapter_blocks[1:]:
        end_brace = block.find('}')
        if end_brace != -1:
            title = block[:end_brace].strip()
            # The content might end where another \documentclass or \chapter begins, but we already split by \chapter
            # Just ignore \documentclass and \begin{document} etc inside the body
            body = block[end_brace+1:]
            
            # Clean up unwanted LaTeX preamble/postamble artifacts inside the body
            body = re.sub(r'\\documentclass\[.*?\]\{.*?\}', '', body)
            body = re.sub(r'\\begin\{document\}', '', body)
            body = re.sub(r'\\end\{document\}', '', body)
            body = re.sub(r'% =============================================================================', '', body)
            
            parts[title] = body.strip()
            
    # Now for white box testing
    wb_content = open('white_box_testing.tex', 'r', encoding='utf-8').read()
    wb_blocks = wb_content.split('\\chapter{')
    for block in wb_blocks[1:]:
        end_brace = block.find('}')
        if end_brace != -1:
            title = block[:end_brace].strip()
            body = block[end_brace+1:]
            body = re.sub(r'\\end\{document\}', '', body)
            parts['WB: ' + title] = body.strip()
            
    return parts

def write_latex():
    parts = parse_tex_files()
    
    out = open('STOCKLY_COMPREHENSIVE_REPORT.tex', 'w', encoding='utf-8')
    
    out.write(r'''\documentclass[12pt,a4paper]{report}

% ─── Packages ────────────────────────────────────────────────────────────────
\usepackage[a4paper, margin=2.5cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{microtype}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{tabularx}
\usepackage{multirow}
\usepackage{enumitem}
\usepackage{listings}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{tocloft}
\usepackage{hyperref}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{tikz}
\usepackage{pgf}
\usetikzlibrary{shapes.geometric, arrows.meta, positioning, fit, backgrounds, calc}
\usepackage{mdframed}
\usepackage{tcolorbox}
\tcbuselibrary{skins, breakable}
\usepackage{fontawesome5}
\usepackage{setspace}
\usepackage{caption}
\usepackage{subcaption}

% ─── Custom Styles ────────────────────────────────────────────────────────────
\definecolor{primary}{HTML}{1E3A5F}
\definecolor{secondary}{HTML}{2E86AB}
\definecolor{accent}{HTML}{E84855}
\definecolor{success}{HTML}{3BB273}
\definecolor{warning}{HTML}{F4A261}
\definecolor{lightgray}{HTML}{F5F5F5}
\definecolor{darkgray}{HTML}{333333}
\definecolor{codebg}{HTML}{1E1E2E}
\definecolor{codetext}{HTML}{CDD6F4}
\definecolor{p1red}{HTML}{C0392B}

\lstdefinestyle{codestyle}{
  backgroundcolor=\color{codebg},
  basicstyle=\ttfamily\small\color{codetext},
  keywordstyle=\color{accent}\bfseries,
  commentstyle=\color{success}\itshape,
  stringstyle=\color{warning},
  breaklines=true,
  frame=single,
  rulecolor=\color{secondary},
  numbers=left,
  numberstyle=\tiny\color{darkgray},
  tabsize=2,
  showstringspaces=false,
}
\lstset{style=codestyle}

\tcbset{
  testbox/.style={
    enhanced, breakable,
    colback=lightgray, colframe=secondary,
    fonttitle=\bfseries\color{white},
    coltitle=white, attach boxed title to top left,
    boxed title style={colback=secondary, rounded corners},
    rounded corners, drop shadow,
  },
  criticalbox/.style={
    enhanced, breakable,
    colback=red!5, colframe=p1red,
    fonttitle=\bfseries\color{white},
    coltitle=white, attach boxed title to top left,
    boxed title style={colback=p1red, rounded corners},
    rounded corners,
  },
  infobox/.style={
    enhanced, breakable,
    colback=blue!5, colframe=primary,
    fonttitle=\bfseries\color{white},
    coltitle=white, attach boxed title to top left,
    boxed title style={colback=primary, rounded corners},
    rounded corners,
  },
  warningbox/.style={
    enhanced, breakable,
    colback=orange!8, colframe=warning,
    fonttitle=\bfseries\color{white},
    coltitle=white, attach boxed title to top left,
    boxed title style={colback=warning, rounded corners},
    rounded corners,
  },
}

\tikzset{
  startstop/.style={
    rectangle, rounded corners=8pt,
    minimum width=3cm, minimum height=0.9cm,
    text centered, draw=primary, very thick,
    fill=primary!15, font=\small\bfseries,
  },
  process/.style={
    rectangle,
    minimum width=3.5cm, minimum height=0.9cm,
    text centered, draw=secondary, thick,
    fill=secondary!10, font=\small,
  },
  decision/.style={
    diamond, aspect=2.2,
    minimum width=3.5cm, minimum height=0.9cm,
    text centered, draw=accent, thick,
    fill=accent!10, font=\small,
  },
  io/.style={
    trapezium, trapezium left angle=70, trapezium right angle=110,
    minimum width=3cm, minimum height=0.9cm,
    text centered, draw=success, thick,
    fill=success!10, font=\small,
  },
  terminal/.style={
    rectangle, rounded corners=15pt,
    minimum width=2.5cm, minimum height=0.9cm,
    text centered, draw=accent, very thick,
    fill=accent!20, font=\small\bfseries,
  },
  arrow/.style={-{Stealth[length=6pt]}, thick, color=darkgray},
  yes/.style={font=\small\color{success}\bfseries},
  no/.style={font=\small\color{accent}\bfseries},
}
\newcommand{\pone}{\textbf{\color{p1red}P1}}
\newcommand{\ptwo}{\textbf{\color{p2orange}P2}}
\newcommand{\pthree}{\textbf{\color{p3blue}P3}}
\newcommand{\pfour}{\textbf{\color{p4green}P4}}

\setlength{\parskip}{6pt}
\setlength{\parindent}{0pt}

\begin{document}
''')

    # Title Page
    out.write(r'''
\begin{titlepage}
\begin{center}
    \vspace*{1.5cm}
    
    {\fontsize{20}{24}\selectfont \textbf{Indian Institute of Information Technology, Vadodara}}\\[2cm]
    
    {\fontsize{24}{28}\selectfont \textbf{INVENTORY \& SUPPLY CHAIN MANAGEMENT SYSTEM}}\\[2cm]
    
    {\Large \textbf{A Project Report}}\\[3cm]
    
    {\large \textbf{Submitted by:}}\\[0.5cm]
    {\large Ashay Gupta (202451024)}\\[0.2cm]
    {\large Avni Singhal (202451026)}\\[0.2cm]
    {\large Nandish Chauhan (202451040)}\\[0.2cm]
    {\large Arpit Maheshwari (202451022)}\\[3cm]
    
    {\large \textbf{Course: }Software Engineering Lab (CS 264)}\\[0.5cm]
    
    {\large \textbf{Submitted to: }Dr. Pooja Mishra}\\[2cm]
    
\end{center}
\end{titlepage}

''')

    # Abstract
    out.write(r'''
\chapter*{Abstract}
\addcontentsline{toc}{chapter}{Abstract}
This project presents the design and implementation of a web-based Inventory and Supply Chain Management System (Stockly) developed to simplify and modernize the process of inventory tracking, order management, and supply chain operations. Traditional inventory methods are often time-consuming, error-prone, and inefficient. The proposed system provides a secure and automated digital solution that enhances accuracy, transparency, and ease of use.

The system is built with a role-based architecture consisting of multiple users including Admin, Supplier, Retailer, and Client. Users can manage products, coordinate stock allocations across various warehouses, generate comprehensive invoices, and manage orders with integrated stock reservation logic. 

The application utilizes Next.js for a robust frontend and scalable API backend alongside MongoDB and Prisma ORM for efficient data handling and instant synchronization. 

Key features of the system include role-based access control, real-time inventory tracking, intelligent demand forecasting, automated email notifications (via Brevo), and an intuitive dashboard interface. This project demonstrates the effective use of modern web technologies and cloud-based systems to build a reliable and scalable supply chain solution.
\newpage

''')

    # Acknowledgement
    out.write(r'''
\chapter*{Acknowledgement}
\addcontentsline{toc}{chapter}{Acknowledgement}
We would like to express our sincere gratitude to our subject teacher and project guide, Dr. Pooja Mishra, for her continuous support, valuable guidance, and encouragement throughout the development of this project. Her insights and suggestions greatly helped us in improving the quality of our work.

We also extend our thanks to the Teaching Assistants (TAs) for their assistance, timely feedback, and support during the course of this project.

Finally, we would like to thank our institution for providing us with the necessary resources and environment to successfully complete this project.\\[2cm]

\noindent
\textbf{Team Members} \hfill \textbf{Signature:.....................................}
\newpage

''')

    # TOC
    out.write(r'\tableofcontents' + '\n\\newpage\n')
    
    # Define order of chapters
    order = [
        ('Introduction', 'project_report'),
        ('Requirement Analysis', 'project_report'),
        ('Design and Architecture', 'project_report'),
        ('System Diagrams', 'custom'),  # We will generate this
        ('Implementation Details', 'project_report'),
        ('Detailed Implementation Walkthrough', 'project_report'),
        ('Project Management and Development Process', 'project_report'),
        ('Testing and Deployment', 'project_report'),
        ('Performance Analysis and Optimization', 'project_report'),
        ('Comparative Analysis', 'project_report'),
        ('Security Analysis', 'project_report'),
        # White Box Testing chapters
        ('WB: Introduction to White Box Testing', 'white_box'),
        ('WB: Project Architecture Overview', 'white_box'),
        ('WB: Module 1: Authentication \\& Session Management', 'white_box'),
        ('WB: Module 2: Order Management \\& Stock State Machine', 'white_box'),
        ('WB: Module 3: Invoice Generation \\& Financial Logic', 'white_box'),
        ('WB: Module 4: Demand Forecasting Engine', 'white_box'),
        ('WB: Module 5: Email Notification System', 'white_box'),
        ('WB: Module 6: Rate Limiting \\& Caching', 'white_box'),
        ('WB: Module 7: Input Validation (Zod Schemas)', 'white_box'),
        ('WB: Module 8: Role-Based Access Control (RBAC)', 'white_box'),
        ('WB: Module 9: Data Integrity \\& Database Layer', 'white_box'),
        ('WB: Module 10: Stripe Payment \\& Webhook Handling', 'white_box'),
        ('WB: Complete Test Case Matrix', 'white_box'),
        ('WB: Code Coverage Requirements', 'white_box'),
        ('Sample Test Implementations', 'project_report'),
        ('White-Box Testing: Additional Test Cases', 'project_report'),
        ('API Endpoint Detailed Reference', 'project_report'),
        ('Database Schema Reference', 'project_report'),
        ('Conclusion and Future Work', 'project_report'),
        ('References and Bibliography', 'project_report'),
        ('Glossary', 'project_report')
    ]

    for title, source in order:
        if source == 'custom':
            out.write(r'''
\chapter{System Diagrams}
\section{UML Class Diagram}
The UML class diagram provides an overview of the system's core entities and their relationships.
\begin{figure}[h!]
    \centering
    \includegraphics[width=\textwidth]{"Uml_daigram.png"}
    \caption{System UML Class Diagram}
\end{figure}

\section{Entity Relationship Diagram (ERD)}
The ER diagram illustrates the database schema layout and table constraints.
\begin{figure}[h!]
    \centering
    \includegraphics[width=\textwidth]{"erdplus.png"}
    \caption{Entity Relationship Diagram}
\end{figure}

\section{Data Flow Architecture}
The DFA shows how data correctly travels through inputs, processing logic, and outputs.
\begin{figure}[h!]
    \centering
    \includegraphics[width=\textwidth]{"Data Flow Architecture.png"}
    \caption{Data Flow Architecture Diagram}
\end{figure}

\section{Activity Diagram}
The Activity diagram highlights the workflows of users through the different portals.
\begin{figure}[h!]
    \centering
    \includegraphics[width=0.8\textwidth]{"activity_daigram.png"}
    \caption{System Activity Diagram}
\end{figure}

\section{Non-Functional Requirements and Stereotypes}
The following diagram showcases various NFR characteristics mapped across the modules.
\begin{figure}[h!]
    \centering
    \includegraphics[width=0.9\textwidth]{"NFR and Stereotypes.jpeg"}
    \caption{NFR and Stereotypes Diagram}
\end{figure}
''')
        else:
            if title in parts:
                actual_title = title.replace('WB: ', '')
                if actual_title == 'Glossary':
                    # Sometimes chapter macro handles this
                    out.write(f"\n\\chapter*{{{actual_title}}}\n\\addcontentsline{{toc}}{{chapter}}{{{actual_title}}}\n")
                elif actual_title == 'References and Bibliography':
                    out.write(f"\n\\chapter*{{{actual_title}}}\n\\addcontentsline{{toc}}{{chapter}}{{{actual_title}}}\n")
                else:
                    out.write(f"\n\\chapter{{{actual_title}}}\n")
                
                # We replace \chapter contents if they exist inside the block already 
                # (though we split by \chapter, so they don't, but let's be safe)
                out.write(parts[title] + "\n")
            else:
                print(f"Warning: {title} not found!")
    
    out.write(r'\end{document}')
    out.close()

write_latex()
print("Done writing STOCKLY_COMPREHENSIVE_REPORT.tex")
