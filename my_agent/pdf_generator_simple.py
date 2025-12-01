"""
Simple, bulletproof PDF generator using ReportLab.
Converts markdown text to a clean, professional PDF.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


def extract_title_from_markdown(markdown_content):
    """Extract first markdown heading as title."""
    for line in markdown_content.split('\n'):
        line = line.strip()
        if line.startswith('#'):
            return line.lstrip('#').strip()
    return "Report"


def convert_markdown_to_pdf(markdown_content, output_path="report.pdf", metadata=None):
    """
    Convert markdown to PDF using ReportLab.
    
    Args:
        markdown_content: The markdown text
        output_path: Where to save the PDF
        metadata: Dict with 'title', 'author', 'date'
    
    Returns:
        Absolute path to the created PDF
    """
    if metadata is None:
        metadata = {
            "title": "Report",
            "author": "AI Report Generator",
            "date": datetime.now().strftime("%B %d, %Y")
        }
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=1*inch,
    )
    
    # Get default styles and create custom ones
    styles = getSampleStyleSheet()
    
    # Create a fresh style object for custom styles (avoid duplicates)
    custom_styles = {}
    
    custom_styles['Title'] = ParagraphStyle(
        name='Title',
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=8,
        wordWrap='CJK',
        leading=24
    )
    
    custom_styles['Author'] = ParagraphStyle(
        name='Author',
        fontSize=12,
        textColor=colors.HexColor('#555555'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    custom_styles['Date'] = ParagraphStyle(
        name='Date',
        fontSize=11,
        textColor=colors.HexColor('#888888'),
        alignment=TA_CENTER
    )
    
    custom_styles['Heading1'] = ParagraphStyle(
        name='Heading1',
        fontSize=15,
        textColor=colors.HexColor('#1a3a52'),
        spaceBefore=16,
        spaceAfter=10,
        fontName='Helvetica-Bold',
        borderColor=colors.HexColor('#cccccc'),
        borderPadding=8,
        borderWidth=1,
        borderRadius=3
    )
    
    custom_styles['Heading2'] = ParagraphStyle(
        name='Heading2',
        fontSize=13,
        textColor=colors.HexColor('#34495e'),
        spaceBefore=12,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    
    custom_styles['Body'] = ParagraphStyle(
        name='Body',
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        fontName='Times-Roman'
    )
    
    elements = []
    
    # Add cover page
    elements.append(Spacer(1, 1.5*inch))
    elements.append(Paragraph(metadata['title'], custom_styles['Title']))
    elements.append(Paragraph(metadata['author'], custom_styles['Author']))
    elements.append(Paragraph(metadata['date'], custom_styles['Date']))
    elements.append(PageBreak())
    
    # Parse markdown and add to PDF
    for line in markdown_content.split('\n'):
        line_stripped = line.strip()
        
        # Skip empty lines (add small space instead)
        if not line_stripped:
            elements.append(Spacer(1, 8))
            continue
        
        # Handle horizontal rule / section break (---)
        if line_stripped == '---' or line_stripped.startswith('---'):
            elements.append(Spacer(1, 0.2*inch))
            # Add a visual separator line
            from reportlab.platypus import Table, TableStyle
            separator = Table([[''], ], colWidths=[7.5*inch])
            separator.setStyle(TableStyle([
                ('LINEABOVE', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ]))
            elements.append(separator)
            elements.append(Spacer(1, 0.2*inch))
            continue
        
        # H1 Headings - NO automatic page break, add proper spacing before and after
        if line_stripped.startswith('# '):
            text = line_stripped[2:].strip()
            elements.append(Spacer(1, 0.3*inch))  # Generous space before section
            elements.append(Paragraph(text, custom_styles['Heading1']))
            elements.append(Spacer(1, 0.2*inch))  # Space after heading
        
        # H2 Headings - section breaks with spacing
        elif line_stripped.startswith('## '):
            elements.append(Spacer(1, 0.1*inch))
            text = line_stripped[3:].strip()
            elements.append(Paragraph(text, custom_styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))
        
        # H3 Headings
        elif line_stripped.startswith('### '):
            elements.append(Spacer(1, 0.08*inch))
            text = line_stripped[4:].strip()
            elements.append(Paragraph(text, custom_styles['Heading2']))
            elements.append(Spacer(1, 0.08*inch))
        
        else:
            # Regular paragraph - add proper spacing
            elements.append(Paragraph(line_stripped, custom_styles['Body']))
    
    # Build PDF
    try:
        doc.build(elements)
        abs_path = os.path.abspath(output_path)
        print(f"  [PDF] Successfully created: {abs_path}")
        return abs_path
    except Exception as e:
        print(f"  [PDF] Error: {e}")
        raise


if __name__ == "__main__":
    # Test
    test_md = "# Test Report\n\nThis is a test.\n\n## Section\n\nContent here."
    convert_markdown_to_pdf(test_md, "test.pdf")
