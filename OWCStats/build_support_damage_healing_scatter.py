from build_owcs_player_scatter import build_chart


if __name__ == "__main__":
    svg_path, row_count = build_chart("support")
    print(f"SVG written: {svg_path}")
    print(f"Players: {row_count}")
