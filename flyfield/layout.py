import logging
from collections import defaultdict
from .config import GAP_THRESHOLD
from .utils import clean_fill_string, format_money

logger = logging.getLogger(__name__)


def calculate_layout_fields(boxes):
    """
    Annotate boxes with layout metadata: assign IDs, lines, blocks,
    calculate block dimensions, and concatenate fill text per block.

    Monetary fields are formatted in the block starting boxes based on field_type.

    Args:
        boxes (list): List of box dicts, assumed sorted by page and vertical order.

    Returns:
        dict: Mapping page numbers to lists of boxes with layout annotations.
    """
    epsilon = 1  # Vertical tolerance for grouping boxes into the same line

    idx = 0
    current_page = None
    line_counter = 1

    while idx < len(boxes):
        page_num = boxes[idx]["page_num"]
        if page_num != current_page:
            current_page = page_num
            line_counter = 1
        block_id_counter = 1

        # Initialize first box in a new line and block

        boxes[idx].update(
            {
                "id": idx + 1,
                "line": line_counter,
                "block_start": block_id_counter,
                "block": block_id_counter,
                "code": f"{page_num}-{line_counter}-{block_id_counter}",
                "pgap": None,  # Gap before this box (none for first)
            }
        )

        block_start = idx
        j = idx + 1

        # Group boxes horizontally on the same line by bottom alignment and gap thresholds

        while (
            j < len(boxes)
            and boxes[j]["page_num"] == page_num
            and abs(boxes[j]["bottom"] - boxes[idx]["bottom"]) < epsilon
        ):
            boxes[j]["id"] = j + 1
            boxes[j]["line"] = line_counter

            prev_gap = round(boxes[j]["x0"] - boxes[j - 1]["x1"], 1)
            boxes[j]["pgap"] = prev_gap
            boxes[j - 1]["gap"] = prev_gap

            if prev_gap >= GAP_THRESHOLD:
                # Close current block and start a new block

                end_idx = j - 1
                block_length = (end_idx - block_start) + 1
                block_width = round(boxes[end_idx]["x1"] - boxes[block_start]["x0"], 1)
                boxes[block_start]["block_length"] = block_length
                boxes[block_start]["block_width"] = block_width

                current_box = boxes[block_start]
                if current_box.get("field_type") not in ("DollarCents", "Dollars"):
                    raw_fill = " ".join(
                        box.get("fill", "") for box in boxes[block_start : end_idx + 1]
                    )
                    boxes[block_start]["block_fill"] = clean_fill_string(raw_fill)
                else:
                    decimal_flag = current_box.get("field_type") == "DollarCents"
                    current_box["fill"] = format_money(
                        current_box["fill"], decimal=decimal_flag
                    )
                block_id_counter += 1
                block_start = j

                boxes[j].update(
                    {
                        "block_start": block_id_counter,
                        "block": block_id_counter,
                        "code": f"{page_num}-{line_counter}-{block_id_counter}",
                    }
                )
            else:
                # Continue current block

                boxes[j].update(
                    {
                        "block_start": block_id_counter,
                        "block": block_id_counter,
                        "code": f"{page_num}-{line_counter}-{block_id_counter}",
                    }
                )
            j += 1
        # Close last block on the line

        end_idx = j - 1
        block_length = (end_idx - block_start) + 1
        block_width = round(boxes[end_idx]["x1"] - boxes[block_start]["x0"], 1)
        boxes[block_start]["block_length"] = block_length
        boxes[block_start]["block_width"] = block_width

        current_box = boxes[block_start]
        if current_box.get("field_type") not in ("DollarCents", "Dollars"):
            raw_fill = " ".join(
                box.get("fill", "") for box in boxes[block_start : end_idx + 1]
            )
            boxes[block_start]["block_fill"] = clean_fill_string(raw_fill)
        else:
            decimal_flag = current_box.get("field_type") == "DollarCents"
            current_box["fill"] = format_money(
                current_box["fill"], decimal=decimal_flag
            )
        boxes[end_idx]["gap"] = None  # No gap after the last box in the line

        line_counter += 1
        idx = j
        block_id_counter = 1
    # Group boxes by page number, only include blocks with length >= 1, then sort by line and left coordinate

    page_dict = defaultdict(list)
    for box in boxes:
        if box.get("block_length", 0) >= 1:
            page_dict[box["page_num"]].append(box)
    for page_num in page_dict:
        page_dict[page_num].sort(key=lambda r: (r.get("line", 0), r.get("left", 0)))
    return page_dict


def assign_numeric_blocks(page_dict):
    """
    Merge and assign numeric block types based on proximity and length rules.

    This method modifies the page_dict in place:
    - Merges runs of adjacent blocks of length 3 if gaps between them are small.
    - Optionally prepends certain preceding blocks to runs.
    - Assigns field types "CurrencyDecimal" or "Currency" based on heuristics.
    - Aggregates block lengths, widths, and concatenates fill strings.

    Args:
        page_dict (dict): Dictionary keyed by page numbers containing lists of box dicts.

    Returns:
        dict: The updated page_dict with numeric blocks assigned.
    """
    for page_num, rows in page_dict.items():
        rows.sort(key=lambda r: (r.get("line", 0), r.get("left", 0)))
        page_dict[page_num] = rows
        i = 0
        while i < len(rows):
            block_length = rows[i].get("block_length", 0)
            if block_length == 3:
                run = [rows[i]]
                j = i + 1
                # Collect consecutive blocks of length 3 separated by small gaps

                while j < len(rows):
                    next_block_length = rows[j].get("block_length", 0)
                    next_pgap = rows[j].get("pgap")
                    if (
                        next_block_length == 3
                        and next_pgap is not None
                        and 0 < next_pgap < 8
                    ):
                        run.append(rows[j])
                        j += 1
                    else:
                        break
                # Optionally prepend preceding block if conditions met

                if len(run) >= 2 and i > 0:
                    prev = rows[i - 1]
                    first_pgap = rows[i].get("pgap", 0)
                    if (
                        prev.get("block_length") in (1, 2)
                        and first_pgap is not None
                        and 1 <= first_pgap < 8
                    ):
                        run.insert(0, prev)
                        i -= 1
                next_idx = j
                next_block_length = (
                    rows[next_idx].get("block_length") if next_idx < len(rows) else None
                )
                next_gap = rows[next_idx].get("pgap") if next_idx < len(rows) else None
                if len(run) >= 2:
                    if (
                        next_idx < len(rows)
                        and next_block_length == 2
                        and next_gap is not None
                    ):
                        run.append(rows[next_idx])
                        run[0]["field_type"] = "CurrencyDecimal"
                        j += 1
                    else:
                        run[0]["field_type"] = "Currency"
                    # Aggregate block length and width for the merged block

                    block_length_sum = sum(
                        r.get("block_length", 0) for r in run if r.get("block_length")
                    )
                    run[0]["block_length"] = block_length_sum
                    first_left = min(r.get("left", float("inf")) for r in run)
                    last_left = max(r.get("left", float("-inf")) for r in run)
                    run[0]["block_width"] = (
                        last_left - first_left + run[-1]["block_width"]
                    )
                    fills = [
                        r.get("block_fill", "") for r in run if r.get("block_fill")
                    ]
                    run[0]["block_fill"] = "".join(fills).strip()
                    # Clear subordinate blocks lengths and fills

                    for r in run[1:]:
                        r["block_length"] = None
                        r["block_width"] = None
                        r["block_fill"] = None
                i = j
            else:
                i += 1
    return page_dict
