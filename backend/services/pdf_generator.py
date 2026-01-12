"""
Professional PDF Generator - Modern Document Design System
Created by: Senior Python Developer & Document Design Expert
Purpose: Generate aesthetically pleasing, professional documents with modern typography
"""

import os
import datetime
from io import BytesIO
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image, PageBreak, KeepTogether, CondPageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.flowables import HRFlowable

# =============================================================================
# FONT REGISTRATION & MODERN COLOR PALETTE
# =============================================================================

# Register professional fonts with fallback handling
def register_fonts():
    """Register professional fonts with graceful fallback"""
    try:
        # Professional font pairing: Helvetica (headers) + Times (body)
        pdfmetrics.registerFont(TTFont('Helvetica', 'Helvetica'))
        pdfmetrics.registerFont(TTFont('Helvetica-Bold', 'Helvetica-Bold'))
        pdfmetrics.registerFont(TTFont('Helvetica-Oblique', 'Helvetica-Oblique'))
        pdfmetrics.registerFont(TTFont('Times-Roman', 'Times-Roman'))
        pdfmetrics.registerFont(TTFont('Times-Bold', 'Times-Bold'))
        pdfmetrics.registerFont(TTFont('Times-Italic', 'Times-Italic'))
        return True
    except:
        # Fallback to default fonts
        return False

# Modern, sophisticated color palette
@dataclass
class ColorPalette:
    """Professional color palette for modern documents"""
    # Primary brand colors
    primary: colors.Color = colors.HexColor('#1e293b')      # Deep slate
    secondary: colors.Color = colors.HexColor('#334155')    # Medium slate
    accent: colors.Color = colors.HexColor('#3b82f6')       # Modern blue
    
    # Text colors
    text_primary: colors.Color = colors.HexColor('#1e293b')  # Primary text
    text_secondary: colors.Color = colors.HexColor('#64748b') # Secondary text
    text_muted: colors.Color = colors.HexColor('#94a3b8')     # Muted text
    
    # Background and borders
    background: colors.Color = colors.HexColor('#f8fafc')     # Light background
    background_alt: colors.Color = colors.HexColor('#f1f5f9') # Alt background
    border: colors.Color = colors.HexColor('#e2e8f0')        # Subtle borders
    white: colors.Color = colors.white
    
    # Status colors
    success: colors.Color = colors.HexColor('#10b981')       # Green
    warning: colors.Color = colors.HexColor('#f59e0b')       # Orange
    error: colors.Color = colors.HexColor('#ef4444')         # Red

# Global color palette instance
COLORS = ColorPalette()

# =============================================================================
# CENTRALIZED STYLESHEET SYSTEM
# =============================================================================

def get_stylesheet() -> Dict[str, ParagraphStyle]:
    """
    Centralized stylesheet with professional typography hierarchy
    Returns: Dictionary of named ParagraphStyle objects
    """
    fonts_registered = register_fonts()
    styles = getSampleStyleSheet()
    
    # Clear any existing custom styles to avoid conflicts
    # StyleSheet1 doesn't have .keys() method, so we need to handle this differently
    existing_styles = []
    for name in ['CustomTitle', 'CustomSubtitle', 'CustomHeading1', 'CustomHeading2', 
                 'CustomBodyText', 'CustomQuote', 'CustomFooter', 'CustomTableHeader',
                 'CustomTOC1', 'CustomTOC2', 'CustomListItem', 'CustomMetadata']:
        if name in styles:
            existing_styles.append(name)
    
    # Remove existing custom styles
    for name in existing_styles:
        if name in styles:
            del styles[name]
    
    # === TYPOGRAPHIC HIERARCHY ===
    
    # 1. Document Title - Most prominent
    styles.add(ParagraphStyle(
        'ProfessionalTitle',
        parent=styles['Heading1'],
        fontSize=32,
        leading=40,
        spaceBefore=48,
        spaceAfter=24,
        textColor=COLORS.primary,
        fontName='Helvetica-Bold' if fonts_registered else 'Helvetica-Bold',
        alignment=TA_CENTER,
        borderWidth=0,
        keepWithNext=False
    ))
    
    # 2. Document Subtitle - Elegant secondary
    styles.add(ParagraphStyle(
        'ProfessionalSubtitle',
        parent=styles['Heading2'],
        fontSize=20,
        leading=26,
        spaceBefore=12,
        spaceAfter=32,
        textColor=COLORS.text_secondary,
        fontName='Helvetica-Oblique' if fonts_registered else 'Helvetica-Oblique',
        alignment=TA_CENTER,
        borderWidth=0
    ))
    
    # 3. Heading 1 - Main section headers
    styles.add(ParagraphStyle(
        'ProfessionalHeading1',
        parent=styles['Heading1'],
        fontSize=24,
        leading=32,
        spaceBefore=36,
        spaceAfter=16,
        textColor=COLORS.primary,
        fontName='Helvetica-Bold' if fonts_registered else 'Helvetica-Bold',
        alignment=TA_LEFT,
        borderWidth=0,
        borderColor=COLORS.border,
        keepWithNext=True  # Prevent orphaned headers
    ))
    
    # 4. Heading 2 - Subsection headers
    styles.add(ParagraphStyle(
        'ProfessionalHeading2',
        parent=styles['Heading2'],
        fontSize=18,
        leading=24,
        spaceBefore=24,
        spaceAfter=12,
        textColor=COLORS.secondary,
        fontName='Helvetica-Bold' if fonts_registered else 'Helvetica-Bold',
        alignment=TA_LEFT,
        borderWidth=0,
        keepWithNext=True  # Prevent orphaned headers
    ))
    
    # 5. Heading 3 - Tertiary headers
    styles.add(ParagraphStyle(
        'ProfessionalHeading3',
        parent=styles['Heading3'],
        fontSize=14,
        leading=20,
        spaceBefore=16,
        spaceAfter=8,
        textColor=COLORS.text_primary,
        fontName='Helvetica-Bold' if fonts_registered else 'Helvetica-Bold',
        alignment=TA_LEFT,
        borderWidth=0,
        keepWithNext=True
    ))
    
    # 6. Body Text - Main content
    styles.add(ParagraphStyle(
        'ProfessionalBodyText',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,  # Professional line height (1.45x font size)
        spaceAfter=8,
        textColor=COLORS.text_primary,
        fontName='Times-Roman' if fonts_registered else 'Times-Roman',
        alignment=TA_JUSTIFY,
        firstLineIndent=24,  # Professional paragraph indentation
        borderWidth=0,
        hyphenation=True
    ))
    
    # 7. Body Text No Indent - For lists and special content
    styles.add(ParagraphStyle(
        'ProfessionalBodyTextNoIndent',
        parent=styles['ProfessionalBodyText'],
        firstLineIndent=0,
        spaceAfter=6
    ))
    
    # 8. Quote Style - Elegant block quotes
    styles.add(ParagraphStyle(
        'ProfessionalQuote',
        parent=styles['Normal'],
        fontSize=11,
        leading=18,
        spaceBefore=20,
        spaceAfter=20,
        textColor=COLORS.text_secondary,
        fontName='Times-Italic' if fonts_registered else 'Times-Italic',
        leftIndent=36,
        rightIndent=36,
        borderLeftWidth=3,
        borderLeftColor=COLORS.accent,
        borderLeftPadding=18,
        backColor=COLORS.background,
        alignment=TA_JUSTIFY
    ))
    
    # 9. Caption Style - For tables and figures
    styles.add(ParagraphStyle(
        'ProfessionalCaption',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        spaceBefore=6,
        spaceAfter=12,
        textColor=COLORS.text_muted,
        fontName='Helvetica-Oblique' if fonts_registered else 'Helvetica-Oblique',
        alignment=TA_CENTER
    ))
    
    # 10. Metadata Style - For secondary information
    styles.add(ParagraphStyle(
        'ProfessionalMetadata',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=6,
        textColor=COLORS.text_secondary,
        fontName='Helvetica' if fonts_registered else 'Helvetica',
        alignment=TA_LEFT
    ))
    
    # 11. TOC Styles - Table of Contents hierarchy
    styles.add(ParagraphStyle(
        'ProfessionalTOC1',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        spaceBefore=12,
        spaceAfter=6,
        textColor=COLORS.text_primary,
        fontName='Helvetica-Bold' if fonts_registered else 'Helvetica-Bold',
        alignment=TA_LEFT,
        leftIndent=0
    ))
    
    styles.add(ParagraphStyle(
        'ProfessionalTOC2',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceBefore=6,
        spaceAfter=4,
        textColor=COLORS.text_primary,
        fontName='Helvetica' if fonts_registered else 'Helvetica',
        alignment=TA_LEFT,
        leftIndent=24
    ))
    
    styles.add(ParagraphStyle(
        'ProfessionalTOC3',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        spaceBefore=4,
        spaceAfter=3,
        textColor=COLORS.text_secondary,
        fontName='Helvetica' if fonts_registered else 'Helvetica',
        alignment=TA_LEFT,
        leftIndent=48
    ))
    
    return styles

# =============================================================================
# DYNAMIC INDENTATION HELPER FUNCTIONS
# =============================================================================

def create_indented_style(
    base_style_name: str, 
    indent_level: int = 1, 
    indent_amount: float = 20,
    styles: Optional[Dict[str, ParagraphStyle]] = None
) -> ParagraphStyle:
    """
    Create dynamically indented styles using .clone() method
    Prevents leftIndent type errors and ensures proper inheritance
    
    Args:
        base_style_name: Name of the base style to clone
        indent_level: Number of indentation levels
        indent_amount: Pixels to indent per level
        styles: Stylesheet dictionary (uses get_stylesheet() if None)
    
    Returns:
        New ParagraphStyle with applied indentation
    """
    if styles is None:
        styles = get_stylesheet()
    
    base_style = styles[base_style_name]
    total_indent = indent_level * indent_amount
    
    # Clone the base style to maintain all properties
    new_style = ParagraphStyle(
        f'{base_style_name}_Indented_{indent_level}',
        parent=base_style,
        leftIndent=total_indent
    )
    
    return new_style

def create_list_item_style(
    base_style_name: str = 'BodyTextNoIndent',
    bullet_indent: float = 20,
    text_indent: float = 30,
    styles: Optional[Dict[str, ParagraphStyle]] = None
) -> ParagraphStyle:
    """
    Create professional list item styles with proper bullet alignment
    
    Args:
        base_style_name: Base style for list items
        bullet_indent: Indent for bullet points
        text_indent: Indent for text content
        styles: Stylesheet dictionary
    
    Returns:
        New ParagraphStyle configured for list items
    """
    if styles is None:
        styles = get_stylesheet()
    
    base_style = styles[base_style_name]
    
    list_style = ParagraphStyle(
        f'{base_style_name}_ListItem',
        parent=base_style,
        leftIndent=text_indent,
        bulletIndent=bullet_indent,
        spaceAfter=4
    )
    
    return list_style

# =============================================================================
# ADVANCED TABLE STYLING
# =============================================================================

def create_professional_table(
    data: List[List[str]], 
    col_widths: Optional[List[float]] = None,
    style_options: Optional[Dict[str, Any]] = None
) -> Table:
    """
    Create professionally styled tables with advanced features
    
    Args:
        data: Table data (list of lists)
        col_widths: Column widths (auto-calculated if None)
        style_options: Additional styling options
    
    Returns:
        Styled Table object
    """
    if not data:
        return None
    
    # Default style options
    default_options = {
        'header_bg': COLORS.primary,
        'header_text': COLORS.white,
        'body_bg': COLORS.white,
        'body_alt_bg': COLORS.background,
        'border_color': COLORS.border,
        'text_color': COLORS.text_primary,
        'header_font': 'Helvetica-Bold',
        'body_font': 'Times-Roman',
        'header_size': 11,
        'body_size': 10,
        'padding': 8,
        'zebra_striping': True
    }
    
    # Merge with provided options
    if style_options:
        default_options.update(style_options)
    
    opts = default_options
    
    # Calculate column widths if not provided
    if col_widths is None:
        # Intelligent width calculation based on content
        total_width = 7 * inch  # Standard page width minus margins
        col_count = len(data[0])
        col_widths = [total_width / col_count] * col_count
    
    # Build comprehensive table style
    table_style = []
    
    # Header styling
    table_style.extend([
        ('BACKGROUND', (0, 0), (-1, 0), opts['header_bg']),
        ('TEXTCOLOR', (0, 0), (-1, 0), opts['header_text']),
        ('FONTNAME', (0, 0), (-1, 0), opts['header_font']),
        ('FONTSIZE', (0, 0), (-1, 0), opts['header_size']),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, 0), opts['padding']),
        ('BOTTOMPADDING', (0, 0), (-1, 0), opts['padding']),
        ('LEFTPADDING', (0, 0), (-1, 0), opts['padding']),
        ('RIGHTPADDING', (0, 0), (-1, 0), opts['padding']),
    ])
    
    # Body styling
    table_style.extend([
        ('FONTNAME', (0, 1), (-1, -1), opts['body_font']),
        ('FONTSIZE', (0, 1), (-1, -1), opts['body_size']),
        ('TEXTCOLOR', (0, 1), (-1, -1), opts['text_color']),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), opts['padding']),
        ('BOTTOMPADDING', (0, 1), (-1, -1), opts['padding']),
        ('LEFTPADDING', (0, 1), (-1, -1), opts['padding']),
        ('RIGHTPADDING', (0, 1), (-1, -1), opts['padding']),
    ])
    
    # Zebra striping
    if opts['zebra_striping']:
        for i in range(1, len(data)):
            if i % 2 == 0:  # Even rows
                table_style.append(('BACKGROUND', (0, i), (-1, i), opts['body_alt_bg']))
    
    # Borders and grid
    table_style.extend([
        ('GRID', (0, 0), (-1, -1), 0.5, opts['border_color']),
        ('BOX', (0, 0), (-1, -1), 1, opts['border_color']),
        ('LINEBELOW', (0, 0), (-1, 0), 2, opts['header_bg']),  # Header bottom line
    ])
    
    # Create and style the table
    table = Table(data, colWidths=col_widths, repeatRows=1)  # Repeat header on page breaks
    table.setStyle(TableStyle(table_style))
    
    return table

# =============================================================================
# PROFESSIONAL HEADER/FOOTER SYSTEM
# =============================================================================

def create_header_footer(canvas, doc, title: str, subtitle: str = ""):
    """
    Professional header and footer with consistent branding
    
    Args:
        canvas: ReportLab canvas object
        doc: Document template
        title: Document title
        subtitle: Document subtitle
    """
    canvas.saveState()
    
    # Page dimensions
    page_width = doc.width + doc.leftMargin + doc.rightMargin
    page_height = doc.height + doc.topMargin + doc.bottomMargin
    
    # === HEADER ===
    header_height = 60
    header_y = page_height - doc.topMargin - header_height
    
    # Header background
    canvas.setFillColor(COLORS.background)
    canvas.rect(doc.leftMargin, header_y, doc.width, header_height, fill=1, stroke=0)
    
    # Header separator line
    canvas.setStrokeColor(COLORS.border)
    canvas.setLineWidth(1)
    canvas.line(doc.leftMargin, header_y, doc.leftMargin + doc.width, header_y)
    
    # Logo placeholder (professional circle)
    logo_x = doc.leftMargin + 20
    logo_y = header_y + header_height // 2
    canvas.setFillColor(COLORS.accent)
    canvas.circle(logo_x, logo_y, 12, fill=1, stroke=0)
    canvas.setFillColor(COLORS.white)
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawCentredString(logo_x, logo_y - 3, 'LOGO')
    
    # Document title and subtitle
    title_x = logo_x + 35
    canvas.setFont('Helvetica-Bold', 14)
    canvas.setFillColor(COLORS.primary)
    canvas.drawString(title_x, header_y + header_height - 20, title)
    
    if subtitle:
        canvas.setFont('Helvetica', 10)
        canvas.setFillColor(COLORS.text_secondary)
        canvas.drawString(title_x, header_y + header_height - 38, subtitle)
    
    # === FOOTER ===
    footer_height = 30
    footer_y = doc.bottomMargin
    
    # Footer background
    canvas.setFillColor(COLORS.background)
    canvas.rect(doc.leftMargin, footer_y, doc.width, footer_height, fill=1, stroke=0)
    
    # Footer separator line
    canvas.setStrokeColor(COLORS.border)
    canvas.setLineWidth(1)
    canvas.line(doc.leftMargin, footer_y + footer_height, doc.leftMargin + doc.width, footer_y + footer_height)
    
    # Footer content
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(COLORS.text_muted)
    
    # Page number (left)
    page_text = f"Page {doc.page}"
    canvas.drawString(doc.leftMargin + 20, footer_y + 10, page_text)
    
    # Timestamp (center)
    timestamp = datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')
    canvas.drawCentredString(page_width / 2, footer_y + 10, f"Generated on {timestamp}")
    
    # Confidentiality notice (right)
    canvas.setFont('Helvetica-Oblique', 9)
    canvas.drawString(page_width - 100, footer_y + 10, "Confidential")
    
    canvas.restoreState()

# =============================================================================
# SPACING AND LAYOUT HELPERS
# =============================================================================

def add_section_spacing(story: List, before: float = 12, after: float = 12):
    """Add professional spacing around sections"""
    if before > 0:
        story.append(Spacer(1, before))
    if after > 0:
        story.append(Spacer(1, after))

def create_section_break(story: List, height: float = 24):
    """Add a section break with visual separator"""
    story.append(Spacer(1, height))
    story.append(HRFlowable(width='80%', thickness=1, color=COLORS.border, spaceBefore=6, spaceAfter=6))
    story.append(Spacer(1, height))

def keep_header_with_content(header: Paragraph, content_elements: List) -> KeepTogether:
    """
    Prevent headers from being orphaned at bottom of pages
    Uses KeepTogether to ensure header stays with following content
    """
    elements = [header, Spacer(1, 8)]
    elements.extend(content_elements)
    return KeepTogether(elements)

# =============================================================================
# MAIN DOCUMENT BUILDER
# =============================================================================

class ProfessionalDocumentBuilder:
    """
    High-level document builder for professional PDF generation
    Manages the "Story" (list of Flowables) with proper architecture
    """
    
    def __init__(self, page_size=A4, margins: Optional[Dict[str, float]] = None):
        """
        Initialize document builder
        
        Args:
            page_size: Page size (A4, letter, etc.)
            margins: Dictionary with 'left', 'right', 'top', 'bottom' margins in cm
        """
        self.page_size = page_size
        
        # Professional margins (default)
        default_margins = {'left': 2.0, 'right': 2.0, 'top': 2.5, 'bottom': 2.0}
        if margins:
            default_margins.update(margins)
        
        self.margins = default_margins
        self.styles = get_stylesheet()
        self.story = []  # Strict management as list of Flowables
        
        # Document metadata
        self.title = ""
        self.subtitle = ""
        self.author = ""
        self.subject = ""
    
    def set_metadata(self, title: str, subtitle: str = "", author: str = "", subject: str = ""):
        """Set document metadata"""
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.subject = subject
    
    def add_title_page(self):
        """Add professional title page"""
        self.story.append(Spacer(1, 2 * inch))
        self.story.append(Paragraph(self.title, self.styles['ProfessionalTitle']))
        
        if self.subtitle:
            self.story.append(Spacer(1, 0.5 * inch))
            self.story.append(Paragraph(self.subtitle, self.styles['ProfessionalSubtitle']))
        
        self.story.append(Spacer(1, 1.5 * inch))
        self.story.append(PageBreak())
    
    def add_heading(self, text: str, level: int = 1, keep_with_next: bool = True):
        """Add heading with proper hierarchy and orphan prevention"""
        style_name = f'ProfessionalHeading{level}'
        heading = Paragraph(text, self.styles[style_name])
        
        if keep_with_next:
            # Will be followed by content, use KeepTogether
            self.story.append(heading)  # Content should be added separately with keep_header_with_content
        else:
            self.story.append(heading)
        
        add_section_spacing(self.story, before=0, after=8)
    
    def add_paragraph(self, text: str, style_name: str = 'ProfessionalBodyText', keep_with_next: bool = False):
        """Add paragraph with specified style"""
        para = Paragraph(text, self.styles[style_name])
        
        if keep_with_next:
            self.story.append(KeepTogether([para]))
        else:
            self.story.append(para)
    
    def add_table(self, data: List[List[str]], style_options: Optional[Dict[str, Any]] = None, caption: str = ""):
        """Add professionally styled table with optional caption"""
        table = create_professional_table(data, style_options=style_options)
        
        if table:
            # Keep table with caption if provided
            if caption:
                table_elements = [table, Spacer(1, 6), Paragraph(caption, self.styles['ProfessionalCaption'])]
                self.story.append(KeepTogether(table_elements))
            else:
                self.story.append(table)
            
            add_section_spacing(self.story, after=16)
    
    def add_toc_entry(self, text: str, level: int = 1, page_ref: str = ""):
        """Add table of contents entry with proper indentation"""
        style_name = f'ProfessionalTOC{level}'
        toc_text = f"{text} {page_ref}" if page_ref else text
        self.story.append(Paragraph(toc_text, self.styles[style_name]))
        self.story.append(Spacer(1, 4))
    
    def add_section_break(self):
        """Add visual section break"""
        create_section_break(self.story)
    
    def build_pdf(self, output_buffer: Optional[BytesIO] = None) -> bytes:
        """
        Build the PDF document
        
        Args:
            output_buffer: BytesIO buffer (creates new one if None)
        
        Returns:
            PDF content as bytes
        """
        if output_buffer is None:
            output_buffer = BytesIO()
        
        # Create document template
        doc = SimpleDocTemplate(
            output_buffer,
            pagesize=self.page_size,
            leftMargin=self.margins['left'] * cm,
            rightMargin=self.margins['right'] * cm,
            topMargin=self.margins['top'] * cm,
            bottomMargin=self.margins['bottom'] * cm
        )
        
        # Build with professional header/footer
        doc.build(
            self.story,
            onFirstPage=lambda c, d: create_header_footer(c, d, self.title, self.subtitle),
            onLaterPages=lambda c, d: create_header_footer(c, d, self.title, self.subtitle)
        )
        
        output_buffer.seek(0)
        return output_buffer.getvalue()

# =============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# =============================================================================

# These functions maintain backward compatibility with existing code
def get_custom_styles() -> Dict[str, ParagraphStyle]:
    """Legacy compatibility function"""
    return get_stylesheet()

def create_content_table(data: List[List[str]], col_widths: Optional[List[float]] = None, style=None) -> Table:
    """Legacy compatibility function"""
    return create_professional_table(data, col_widths, style)

def create_document_structure(doc, title: str, subtitle: str, content: List):
    """Legacy compatibility function"""
    # This is now handled by ProfessionalDocumentBuilder
    pass
