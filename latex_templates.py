def get_latex_start(title, author):
    latex_start = r'''
    
    \documentclass[14pt]{extarticle}
    \usepackage[utf8]{inputenc}
    \usepackage[T1]{fontenc}
    \usepackage{paracol}
    \usepackage{geometry}
    \geometry{
 a4paper,
 left=5mm,
 right=5mm,
 top=20mm,
 }
    \title{%s}
    \author{%s}
    
    
    \begin{document}
    
    \maketitle
    
    
    \begin{paracol}{2}''' % (title, author)
    return latex_start
    
def get_latex_end():
    latex_end = r'''
    \end{paracol}
    \end{document}
    '''
    return latex_end

    # result = """
    # <!DOCTYPE html>
    # <html>
    #     <head>
    #         %s
    #         <br>
    #         %s
    #     </head>
    #     <body>
    #         %s
    #     </body>
    # </html>
    # """ % (title, author, result)