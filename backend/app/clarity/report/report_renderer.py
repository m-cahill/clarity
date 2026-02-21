"""PDF Report Renderer for CLARITY.

This module provides deterministic PDF generation using ReportLab.

CRITICAL CONSTRAINTS (M11):
1. All rendering must be deterministic (same input → identical bytes).
2. No randomness, no datetime.now, no uuid.
3. No subprocess, no r2l imports.
4. Use only built-in fonts (Helvetica, Courier).
5. Fixed layout, no variable page breaks.
6. Set PDF metadata to fixed values.
7. All floats displayed with 8 decimal places.

The renderer produces:
- Cover page with metadata
- Core metrics summary
- Robustness surface visualization
- Evidence overlay section with heatmap
- Counterfactual probe results
- Reproducibility block
"""

from __future__ import annotations

import io
import re
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Image as RLImage,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.clarity.report.image_renderer import (
    render_heatmap_png,
    render_probe_grid_png,
    render_surface_png,
)
from app.clarity.report.report_model import ClarityReport

if TYPE_CHECKING:
    pass


# Fixed PDF metadata constants
PDF_TITLE = "CLARITY Report"
PDF_AUTHOR = "CLARITY System"
PDF_SUBJECT = "Clinical AI Robustness Evaluation"
PDF_PRODUCER = "CLARITY M11 Report Generator"

# Fixed epoch timestamp for determinism (Unix epoch)
FIXED_TIMESTAMP = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def _format_float(value: float, decimals: int = 8) -> str:
    """Format a float with fixed decimal places.

    Args:
        value: The float value.
        decimals: Number of decimal places.

    Returns:
        Formatted string.
    """
    return f"{value:.{decimals}f}"


class ReportRenderer:
    """Renderer for CLARITY PDF reports.

    This class generates deterministic PDF reports from ClarityReport objects.
    All rendering is fixed-layout with no variable elements.

    Example:
        >>> renderer = ReportRenderer()
        >>> pdf_bytes = renderer.render(report)
    """

    def __init__(self) -> None:
        """Initialize the renderer."""
        self._styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self) -> None:
        """Set up custom paragraph styles."""
        # Title style
        self._title_style = ParagraphStyle(
            "ClarityTitle",
            parent=self._styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            spaceAfter=20,
            alignment=1,  # Center
        )

        # Heading style
        self._heading_style = ParagraphStyle(
            "ClarityHeading",
            parent=self._styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
        )

        # Subheading style
        self._subheading_style = ParagraphStyle(
            "ClaritySubheading",
            parent=self._styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            spaceBefore=15,
            spaceAfter=8,
        )

        # Body style
        self._body_style = ParagraphStyle(
            "ClarityBody",
            parent=self._styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            spaceBefore=4,
            spaceAfter=4,
        )

        # Monospace style
        self._mono_style = ParagraphStyle(
            "ClarityMono",
            parent=self._styles["Code"],
            fontName="Courier",
            fontSize=9,
            spaceBefore=4,
            spaceAfter=4,
        )

    def render(self, report: ClarityReport) -> bytes:
        """Render a ClarityReport to PDF bytes.

        Args:
            report: The report to render.

        Returns:
            PDF file as bytes.
        """
        buffer = io.BytesIO()

        # Create document with fixed margins
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
            title=PDF_TITLE,
            author=PDF_AUTHOR,
            subject=PDF_SUBJECT,
            creator=PDF_PRODUCER,
        )

        # Build story (list of flowables)
        story = []

        # Cover page
        story.extend(self._render_cover_page(report))
        story.append(PageBreak())

        # Core metrics summary
        story.extend(self._render_metrics_section(report))
        story.append(Spacer(1, 20))

        # Robustness surfaces
        story.extend(self._render_robustness_section(report))
        story.append(PageBreak())

        # Evidence overlay section
        story.extend(self._render_overlay_section(report))
        story.append(Spacer(1, 20))

        # Counterfactual results
        story.extend(self._render_probe_section(report))
        story.append(PageBreak())

        # Reproducibility block
        story.extend(self._render_reproducibility_section(report))

        # Build PDF
        doc.build(story, onFirstPage=self._set_metadata, onLaterPages=self._set_metadata)

        # Get raw PDF bytes
        pdf_bytes = buffer.getvalue()

        # Sanitize PDF metadata for determinism
        # ReportLab embeds current timestamps in CreationDate/ModDate - replace with fixed values
        # Parse the generated_at timestamp from metadata
        try:
            creation_date = datetime.fromisoformat(
                report.metadata.generated_at.replace("Z", "+00:00")
            )
        except (ValueError, AttributeError):
            # Fallback to epoch if parsing fails
            creation_date = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        pdf_bytes = self._sanitize_pdf_timestamps(pdf_bytes, creation_date)

        return pdf_bytes

    def _set_metadata(
        self, canvas_obj: canvas.Canvas, doc: SimpleDocTemplate
    ) -> None:
        """Set PDF metadata on each page.

        Uses fixed values from manifest timestamp for determinism.

        Args:
            canvas_obj: ReportLab canvas object.
            doc: Document template.
        """
        # ReportLab sets metadata automatically from SimpleDocTemplate constructor
        pass

    def _sanitize_pdf_timestamps(
        self, pdf_bytes: bytes, creation_date: datetime
    ) -> bytes:
        """Replace non-deterministic PDF timestamps and IDs with fixed values.

        ReportLab embeds:
        1. CreationDate and ModDate using the current system time
        2. A random document ID in the trailer

        This method replaces those with fixed values for determinism.

        Args:
            pdf_bytes: Raw PDF bytes.
            creation_date: Fixed timestamp to use.

        Returns:
            PDF bytes with deterministic metadata.
        """
        # Format the fixed timestamp in PDF date format: D:YYYYMMDDHHmmSS+00'00'
        # Use UTC timezone with explicit +00'00' to be deterministic
        pdf_date = creation_date.strftime("D:%Y%m%d%H%M%S+00'00'")
        pdf_date_bytes = pdf_date.encode("ascii")

        # Pattern to match PDF date strings
        # ReportLab format: D:YYYYMMDDHHMMSS+HH'MM' or D:YYYYMMDDHHMMSS-HH'MM' or D:YYYYMMDDHHMMSSZ
        date_pattern = rb"/CreationDate\s*\(D:\d{14}[+\-Z][^\)]*\)"
        mod_date_pattern = rb"/ModDate\s*\(D:\d{14}[+\-Z][^\)]*\)"

        # Replace CreationDate
        pdf_bytes = re.sub(
            date_pattern,
            b"/CreationDate (" + pdf_date_bytes + b")",
            pdf_bytes,
        )

        # Replace ModDate
        pdf_bytes = re.sub(
            mod_date_pattern,
            b"/ModDate (" + pdf_date_bytes + b")",
            pdf_bytes,
        )

        # Replace the random document ID in the trailer with a fixed value
        # The ID field looks like: /ID \n[<hexstring><hexstring>]
        # We replace it with a deterministic ID based on the timestamp
        fixed_id = creation_date.strftime("%Y%m%d%H%M%S").encode("ascii")
        fixed_id_hex = fixed_id.hex().ljust(32, "0")[:32]  # 32 hex chars
        fixed_id_bytes = f"<{fixed_id_hex}><{fixed_id_hex}>".encode("ascii")

        # Pattern matches: /ID \n[<hex><hex>] with various whitespace
        id_pattern = rb"/ID\s*\n?\s*\[<[0-9a-fA-F]+><[0-9a-fA-F]+>\]"
        pdf_bytes = re.sub(
            id_pattern,
            b"/ID [" + fixed_id_bytes + b"]",
            pdf_bytes,
        )

        return pdf_bytes

    def _render_cover_page(self, report: ClarityReport) -> list:
        """Render the cover page.

        Args:
            report: The report data.

        Returns:
            List of flowables for the cover page.
        """
        elements = []

        # Title
        elements.append(Spacer(1, 100))
        elements.append(Paragraph("CLARITY", self._title_style))
        elements.append(Paragraph(
            "Clinical Localization and Reasoning Integrity Testing",
            self._body_style
        ))
        elements.append(Spacer(1, 40))

        # Report info table
        metadata = report.metadata
        data = [
            ["Case ID", metadata.case_id],
            ["Title", metadata.title],
            ["Generated At", metadata.generated_at],
            ["CLARITY Version", metadata.clarity_version],
            ["R2L SHA", metadata.r2l_sha],
            ["Adapter ID", metadata.adapter_id],
            ["Rich Mode", "Yes" if metadata.rich_mode else "No"],
            ["Sweep Manifest Hash", metadata.sweep_manifest_hash[:16] + "..."],
            ["Serialization Version", metadata.serialization_version],
        ]

        table = Table(data, colWidths=[2.5 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ("ALIGN", (1, 0), (1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(table)

        return elements

    def _render_metrics_section(self, report: ClarityReport) -> list:
        """Render the core metrics summary section.

        Args:
            report: The report data.

        Returns:
            List of flowables.
        """
        elements = []

        elements.append(Paragraph("Core Metrics Summary", self._heading_style))

        metrics = report.metrics
        data = [
            ["Metric", "Value"],
            ["Baseline ESI", _format_float(metrics.baseline_esi)],
            ["Baseline Drift", _format_float(metrics.baseline_drift)],
            ["Global Mean ESI", _format_float(metrics.global_mean_esi)],
            ["Global Mean Drift", _format_float(metrics.global_mean_drift)],
            ["Global ESI Variance", _format_float(metrics.global_variance_esi)],
            ["Global Drift Variance", _format_float(metrics.global_variance_drift)],
        ]

        # Monte Carlo stats
        if metrics.monte_carlo_present and metrics.monte_carlo_entropy is not None:
            data.append(["Monte Carlo Entropy", _format_float(metrics.monte_carlo_entropy)])
        else:
            data.append(["Monte Carlo", "Not present in artifact bundle"])

        table = Table(data, colWidths=[3 * inch, 3 * inch])
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(table)

        return elements

    def _render_robustness_section(self, report: ClarityReport) -> list:
        """Render the robustness surfaces section.

        Args:
            report: The report data.

        Returns:
            List of flowables.
        """
        elements = []

        elements.append(Paragraph("Robustness Surfaces", self._heading_style))

        # Render surface image
        axes_data = [s.to_dict() for s in report.robustness_surfaces]
        if axes_data:
            try:
                img_bytes = render_surface_png(axes_data)
                img_buffer = io.BytesIO(img_bytes)
                img = RLImage(img_buffer, width=5 * inch, height=2 * inch)
                elements.append(img)
            except (ValueError, Exception):
                elements.append(Paragraph(
                    "Surface image could not be rendered.",
                    self._body_style
                ))

        elements.append(Spacer(1, 10))

        # Surface details table for each axis
        for surface in report.robustness_surfaces:
            elements.append(Paragraph(
                f"Axis: {surface.axis}",
                self._subheading_style
            ))

            # Summary row
            summary_data = [
                ["Mean ESI", "Mean Drift", "ESI Variance", "Drift Variance"],
                [
                    _format_float(surface.mean_esi),
                    _format_float(surface.mean_drift),
                    _format_float(surface.variance_esi),
                    _format_float(surface.variance_drift),
                ],
            ]
            summary_table = Table(summary_data, colWidths=[1.5 * inch] * 4)
            summary_table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Courier"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 10))

        return elements

    def _render_overlay_section(self, report: ClarityReport) -> list:
        """Render the evidence overlay section.

        Args:
            report: The report data.

        Returns:
            List of flowables.
        """
        elements = []

        elements.append(Paragraph("Evidence Overlay", self._heading_style))

        overlay = report.overlay_section

        # Render synthetic heatmap if we don't have actual values
        # For demo, we generate a synthetic heatmap visualization
        from app.clarity.report.image_renderer import generate_synthetic_heatmap_values

        try:
            values = generate_synthetic_heatmap_values(
                overlay.image_width,
                overlay.image_height,
                seed=42
            )
            img_bytes = render_heatmap_png(values, width=200, height=200)
            img_buffer = io.BytesIO(img_bytes)
            img = RLImage(img_buffer, width=3 * inch, height=3 * inch)
            elements.append(img)
        except (ValueError, Exception):
            elements.append(Paragraph(
                "Heatmap could not be rendered.",
                self._body_style
            ))

        elements.append(Spacer(1, 10))

        # Region table
        elements.append(Paragraph("Extracted Regions", self._subheading_style))

        if overlay.regions:
            region_data = [["Region ID", "X Range", "Y Range", "Area", "Mean Evidence"]]

            for region in overlay.regions:
                x_range = f"{_format_float(region.x_min, 2)} - {_format_float(region.x_max, 2)}"
                y_range = f"{_format_float(region.y_min, 2)} - {_format_float(region.y_max, 2)}"
                region_data.append([
                    region.region_id,
                    x_range,
                    y_range,
                    _format_float(region.area),
                    _format_float(region.mean_evidence),
                ])

            region_table = Table(
                region_data,
                colWidths=[1.2 * inch, 1.5 * inch, 1.5 * inch, 1.2 * inch, 1.5 * inch]
            )
            region_table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Courier"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            elements.append(region_table)
        else:
            elements.append(Paragraph("No regions extracted.", self._body_style))

        # Total evidence area
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            f"Total Evidence Area: {_format_float(overlay.total_evidence_area)}",
            self._body_style
        ))

        return elements

    def _render_probe_section(self, report: ClarityReport) -> list:
        """Render the counterfactual probe results section.

        Args:
            report: The report data.

        Returns:
            List of flowables.
        """
        elements = []

        elements.append(Paragraph("Counterfactual Probe Results", self._heading_style))

        probe_surface = report.probe_surface

        # Render probe grid image
        probes_data = [p.to_dict() for p in probe_surface.probes]
        if probes_data:
            try:
                img_bytes = render_probe_grid_png(
                    probes_data,
                    probe_surface.grid_size,
                    width=200,
                    height=200
                )
                img_buffer = io.BytesIO(img_bytes)
                img = RLImage(img_buffer, width=3 * inch, height=3 * inch)
                elements.append(img)
                elements.append(Paragraph(
                    "(Blue = negative delta, Red = positive delta)",
                    self._body_style
                ))
            except (ValueError, Exception):
                elements.append(Paragraph(
                    "Probe grid could not be rendered.",
                    self._body_style
                ))

        elements.append(Spacer(1, 10))

        # Summary statistics
        elements.append(Paragraph("Probe Statistics", self._subheading_style))

        stats_data = [
            ["Statistic", "Value"],
            ["Grid Size", f"{probe_surface.grid_size} × {probe_surface.grid_size}"],
            ["Total Probes", str(probe_surface.total_probes)],
            ["Mean Δ ESI", _format_float(probe_surface.mean_delta_esi)],
            ["Mean Δ Drift", _format_float(probe_surface.mean_delta_drift)],
            ["Variance Δ ESI", _format_float(probe_surface.variance_delta_esi)],
            ["Variance Δ Drift", _format_float(probe_surface.variance_delta_drift)],
        ]

        stats_table = Table(stats_data, colWidths=[3 * inch, 3 * inch])
        stats_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTNAME", (1, 1), (1, -1), "Courier"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(stats_table)

        return elements

    def _render_reproducibility_section(self, report: ClarityReport) -> list:
        """Render the reproducibility block.

        Args:
            report: The report data.

        Returns:
            List of flowables.
        """
        elements = []

        elements.append(Paragraph("Reproducibility Block", self._heading_style))

        repro = report.reproducibility

        # Render as monospace block
        content_lines = []
        for key, value in repro.content:
            content_lines.append(f"{key}: {value}")

        block_text = "<br/>".join(content_lines)
        elements.append(Paragraph(block_text, self._mono_style))

        return elements


def render_report_to_pdf(report: ClarityReport) -> bytes:
    """Render a ClarityReport to PDF bytes.

    Convenience function that creates a ReportRenderer and renders.

    Args:
        report: The report to render.

    Returns:
        PDF file as bytes.
    """
    renderer = ReportRenderer()
    return renderer.render(report)

