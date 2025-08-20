#  Created by Martin Strohalm, Thermo Fisher Scientific


LABEL_TAG = """<text x="20" y="12.5" font-family="Arial, Helvetica, Verdana, Liberation Sans, Nimbus Sans" font-size="12" fill="#000" >%s</text>"""

ICON_INFO_SVG = """<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="16">
  
  <path stroke="#6d88cc" stroke-width="1.0" stroke-linecap="round" stroke-linejoin="round" fill="#88aaff" fill-rule="evenodd" d="
    M8.0 0.5 C12.14 0.5 15.5 3.86 15.5 8.0 C15.5 12.14 12.14 15.5 8.0 15.5 C3.86 15.5 0.5 12.14 0.5 8.0 C0.5 3.86 3.86 0.5 8.0 0.5 Z
    " />
  <path stroke="#ffffff" stroke-opacity="0.0" stroke-width="0.0" stroke-linecap="round" stroke-linejoin="round" fill="#000000" fill-opacity="0.6" fill-rule="evenodd" d="
    M8.0 11.9 L6.23 4.49 C6.13 4.06 6.4 3.62 6.83 3.52 C6.89 3.51 6.95 3.5 7.01 3.5 L8.99 3.5 C9.43 3.5 9.79 3.86 9.79 4.3 C9.79 4.36 9.78 4.42 9.77 4.49 L8.78 8.63 C8.68 9.06 8.24 9.33 7.81 9.22 C7.52 9.15 7.29 8.93 7.22 8.63 Z
    M8.0 10.5 C8.55 10.5 9.0 10.95 9.0 11.5 C9.0 12.05 8.55 12.5 8.0 12.5 C7.45 12.5 7.0 12.05 7.0 11.5 C7.0 10.95 7.45 10.5 8.0 10.5 Z
    " />
    
    %s
</svg>"""

ICON_WARNING_SVG = """<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="16">
  
  <path stroke="#cc9600" stroke-width="1.0" stroke-linecap="round" stroke-linejoin="round" fill="#ffbb00" fill-rule="evenodd" d="
    M15.35 13.48 C15.7 14.17 15.42 15.01 14.73 15.35 C14.54 15.45 14.32 15.5 14.11 15.5 L1.89 15.5 C1.12 15.5 0.5 14.88 0.5 14.11 C0.5 13.89 0.55 13.68 0.65 13.48 L6.75 1.27 C7.1 0.58 7.93 0.3 8.62 0.65 C8.89 0.78 9.11 1.0 9.25 1.27 Z
    " />
  <path stroke="#ffffff" stroke-opacity="0.0" stroke-width="0.0" stroke-linecap="round" stroke-linejoin="round" fill="#000000" fill-opacity="0.6" fill-rule="evenodd" d="
    M8.0 13.4 L6.23 5.99 C6.13 5.56 6.4 5.12 6.83 5.02 C6.89 5.01 6.95 5.0 7.01 5.0 L8.99 5.0 C9.43 5.0 9.79 5.36 9.79 5.8 C9.79 5.86 9.78 5.92 9.77 5.99 L8.78 10.13 C8.68 10.56 8.24 10.83 7.81 10.72 C7.52 10.65 7.29 10.43 7.22 10.13 Z
    M8.0 12.0 C8.55 12.0 9.0 12.45 9.0 13.0 C9.0 13.55 8.55 14.0 8.0 14.0 C7.45 14.0 7.0 13.55 7.0 13.0 C7.0 12.45 7.45 12.0 8.0 12.0 Z
    " />
    
    %s
</svg>"""

ICON_ERROR_SVG = """<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="16">
  
  <path stroke="#cc4444" stroke-width="1.0" stroke-linecap="round" stroke-linejoin="round" fill="#ff5555" fill-rule="evenodd" d="
    M15.35 13.48 C15.7 14.17 15.42 15.01 14.73 15.35 C14.54 15.45 14.32 15.5 14.11 15.5 L1.89 15.5 C1.12 15.5 0.5 14.88 0.5 14.11 C0.5 13.89 0.55 13.68 0.65 13.48 L6.75 1.27 C7.1 0.58 7.93 0.3 8.62 0.65 C8.89 0.78 9.11 1.0 9.25 1.27 Z
    " />
  <path stroke="#ffffff" stroke-opacity="0.0" stroke-width="0.0" stroke-linecap="round" stroke-linejoin="round" fill="#000000" fill-opacity="0.6" fill-rule="evenodd" d="
    M8.0 13.4 L6.23 5.99 C6.13 5.56 6.4 5.12 6.83 5.02 C6.89 5.01 6.95 5.0 7.01 5.0 L8.99 5.0 C9.43 5.0 9.79 5.36 9.79 5.8 C9.79 5.86 9.78 5.92 9.77 5.99 L8.78 10.13 C8.68 10.56 8.24 10.83 7.81 10.72 C7.52 10.65 7.29 10.43 7.22 10.13 Z
    M8.0 12.0 C8.55 12.0 9.0 12.45 9.0 13.0 C9.0 13.55 8.55 14.0 8.0 14.0 C7.45 14.0 7.0 13.55 7.0 13.0 C7.0 12.45 7.45 12.0 8.0 12.0 Z
    " />
    
    %s
</svg>"""

ICON_STOP_SVG = """<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="16">
  
  <path stroke="#cc4444" stroke-width="1.0" stroke-linecap="round" stroke-linejoin="round" fill="#ff5555" fill-rule="evenodd" d="
    M15.31 7.25 C15.56 7.72 15.56 8.28 15.31 8.75 L12.3 14.16 C12.03 14.65 11.51 14.95 10.95 14.95 L5.05 14.95 C4.49 14.95 3.97 14.65 3.7 14.16 L0.69 8.75 C0.44 8.28 0.44 7.72 0.69 7.25 L3.7 1.84 C3.97 1.35 4.49 1.05 5.05 1.05 L10.95 1.05 C11.51 1.05 12.03 1.35 12.3 1.84 Z
    " />
  <path stroke="#ffffff" stroke-opacity="0.0" stroke-width="0.0" stroke-linecap="round" stroke-linejoin="round" fill="#000000" fill-opacity="0.6" fill-rule="evenodd" d="
    M8.0 11.9 L6.23 4.49 C6.13 4.06 6.4 3.62 6.83 3.52 C6.89 3.51 6.95 3.5 7.01 3.5 L8.99 3.5 C9.43 3.5 9.79 3.86 9.79 4.3 C9.79 4.36 9.78 4.42 9.77 4.49 L8.78 8.63 C8.68 9.06 8.24 9.33 7.81 9.22 C7.52 9.15 7.29 8.93 7.22 8.63 Z
    M8.0 10.5 C8.55 10.5 9.0 10.95 9.0 11.5 C9.0 12.05 8.55 12.5 8.0 12.5 C7.45 12.5 7.0 12.05 7.0 11.5 C7.0 10.95 7.45 10.5 8.0 10.5 Z
    " />
    
    %s
</svg>"""
