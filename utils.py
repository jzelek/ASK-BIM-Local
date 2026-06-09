import html
import re
from pathlib import Path


def simplify_uri(uri, prefixes):
    """
    Replaces a full URI with its prefix notation.
    """
    for prefix, full_uri in prefixes.items():
        if uri.startswith(full_uri):
            return uri.replace(full_uri, f"{prefix}:")
    return uri

def simplify_nested_dict_with_values(nested_dict, prefixes):
    """
    Applies URI simplification to all keys (and any URI value) in a nested dictionary.
    """
    simplified_dict = {}
    for class_uri, properties in nested_dict.items():
        simplified_class = simplify_uri(class_uri, prefixes)
        simplified_properties = {
            simplify_uri(prop, prefixes): (
                simplify_uri(example, prefixes) if isinstance(example, str) and example.startswith("http") else example
            )
            for prop, example in properties.items()
        }
        simplified_dict[simplified_class] = simplified_properties
    return simplified_dict


def save_kg_diagram(
    nested_dict,
    output_dir="graph_diagrams",
    base_name="kg_context_graph",
    max_properties_per_class=12,
):
    """
    Saves a compact diagram of the class-property KG context.

    The SVG is intended for quick inspection without external rendering tools.
    The Mermaid file keeps a text-based graph source that can be opened in
    Mermaid-compatible viewers for a more interactive graph rendering.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    class_items = sorted(
        nested_dict.items(),
        key=lambda item: (-len(item[1]), item[0]),
    )

    svg_path = output_path / f"{base_name}.svg"
    mermaid_path = output_path / f"{base_name}.mmd"

    _write_kg_svg(svg_path, class_items, max_properties_per_class)
    _write_kg_mermaid(mermaid_path, class_items, max_properties_per_class)

    return {
        "svg": str(svg_path),
        "mermaid": str(mermaid_path),
    }


def _write_kg_svg(svg_path, class_items, max_properties_per_class):
    row_padding = 18
    title_height = 70
    class_box_width = 260
    property_box_width = 560
    x_class = 30
    x_property = 360
    y = title_height
    rows = []

    if not class_items:
        rows.append(
            {
                "class_name": "No classes found",
                "properties": [],
                "omitted": 0,
                "height": 92,
            }
        )
    else:
        for class_name, properties in class_items:
            sorted_properties = sorted(properties.keys())
            visible_properties = sorted_properties[:max_properties_per_class]
            omitted = max(0, len(sorted_properties) - len(visible_properties))
            line_count = max(2, len(visible_properties) + (1 if omitted else 0))
            rows.append(
                {
                    "class_name": class_name,
                    "properties": visible_properties,
                    "omitted": omitted,
                    "height": max(86, 34 + line_count * 18),
                }
            )

    total_height = title_height + sum(row["height"] + row_padding for row in rows) + 20
    total_width = 960

    svg_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{total_height}" viewBox="0 0 {total_width} {total_height}">',
        "<style>",
        ".title { font: 700 24px sans-serif; fill: #1f2937; }",
        ".subtitle { font: 14px sans-serif; fill: #4b5563; }",
        ".class-box { fill: #e0f2fe; stroke: #0369a1; stroke-width: 1.2; }",
        ".prop-box { fill: #f8fafc; stroke: #64748b; stroke-width: 1; }",
        ".class-label { font: 700 14px sans-serif; fill: #0f172a; }",
        ".prop-label { font: 12px monospace; fill: #334155; }",
        ".count-label { font: 12px sans-serif; fill: #475569; }",
        ".edge { stroke: #94a3b8; stroke-width: 1.2; fill: none; }",
        "</style>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="30" y="34" class="title">Knowledge Graph Context Diagram</text>',
        '<text x="30" y="56" class="subtitle">Classes linked to representative properties used for SPARQL generation</text>',
    ]

    for row in rows:
        row_height = row["height"]
        prop_count = len(row["properties"]) + row["omitted"]
        class_label = _truncate(row["class_name"], 32)

        svg_lines.extend(
            [
                f'<rect x="{x_class}" y="{y}" width="{class_box_width}" height="{row_height}" rx="8" class="class-box"/>',
                f'<text x="{x_class + 16}" y="{y + 28}" class="class-label">{html.escape(class_label)}</text>',
                f'<text x="{x_class + 16}" y="{y + 50}" class="count-label">{prop_count} properties</text>',
                f'<path d="M {x_class + class_box_width} {y + row_height / 2:.1f} C {x_class + class_box_width + 34} {y + row_height / 2:.1f}, {x_property - 34} {y + row_height / 2:.1f}, {x_property} {y + row_height / 2:.1f}" class="edge"/>',
                f'<rect x="{x_property}" y="{y}" width="{property_box_width}" height="{row_height}" rx="8" class="prop-box"/>',
            ]
        )

        text_y = y + 24
        if row["properties"]:
            for property_name in row["properties"]:
                label = _truncate(property_name, 72)
                svg_lines.append(
                    f'<text x="{x_property + 16}" y="{text_y}" class="prop-label">{html.escape(label)}</text>'
                )
                text_y += 18
        else:
            svg_lines.append(
                f'<text x="{x_property + 16}" y="{text_y}" class="prop-label">No properties discovered</text>'
            )
            text_y += 18

        if row["omitted"]:
            svg_lines.append(
                f'<text x="{x_property + 16}" y="{text_y}" class="count-label">... {row["omitted"]} more properties</text>'
            )

        y += row_height + row_padding

    svg_lines.append("</svg>")
    svg_path.write_text("\n".join(svg_lines), encoding="utf-8")


def _write_kg_mermaid(mermaid_path, class_items, max_properties_per_class):
    lines = ["graph LR"]
    if not class_items:
        lines.append('  empty["No classes found"]')
    for index, (class_name, properties) in enumerate(class_items):
        class_node = f"class_{index}"
        lines.append(f'  {class_node}["{_escape_mermaid(class_name)}"]')
        for prop_index, property_name in enumerate(sorted(properties.keys())[:max_properties_per_class]):
            property_node = f"{class_node}_prop_{prop_index}"
            lines.append(f'  {property_node}["{_escape_mermaid(property_name)}"]')
            lines.append(f"  {class_node} --> {property_node}")
        omitted = max(0, len(properties) - max_properties_per_class)
        if omitted:
            omitted_node = f"{class_node}_more"
            lines.append(f'  {omitted_node}["... {omitted} more properties"]')
            lines.append(f"  {class_node} --> {omitted_node}")
    mermaid_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _truncate(value, max_length):
    value = str(value)
    if len(value) <= max_length:
        return value
    return value[: max_length - 3] + "..."


def _escape_mermaid(value):
    return re.sub(r'["\\]', "", str(value))


def format_query(raw_query):
    """
    Converts a SPARQL query wrapped with triple backticks into a plain multi-line string.
    """
    if not raw_query:
        return ""

    cleaned_query = raw_query.strip()
    if cleaned_query.startswith("```sparql"):
        cleaned_query = cleaned_query[len("```sparql"):].strip()
    if cleaned_query.startswith("```"):
        cleaned_query = cleaned_query[len("```"):].strip()
    if cleaned_query.endswith("```"):
        cleaned_query = cleaned_query[:-3].strip()
    
    return cleaned_query
