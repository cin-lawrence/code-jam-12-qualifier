from __future__ import annotations
import logging
from dataclasses import dataclass, field
from enum import IntEnum, auto
from typing import Self

from node import Node


logger = logging.getLogger(__name__)


class Mode(IntEnum):
    ID = auto()
    CLASS = auto()
    TAG = auto()


@dataclass
class Selector:
    """
    #id     Selects nodes by their ID attribute.	#topDiv
    .class	Selects nodes by their class attribute.	.container
    tag	    Selects nodes by their tag name (e.g., div, p, h1).	div
    tag.class	Selects nodes by their tag name and class.	div.container
    tag#id	Selects a nodes by their tag name and ID.	div#topDiv
    tag.class#id	Selects nodes by their tag name, class, and ID.	div.container#topDiv
    tag#id.class	Same as above, only reversed (your solution should not care about order)	div#topDiv.container
    tag, tag	Selects nodes by given multiple tag names to match. For example div, p will match both div and p tags.	div, p
    """
    id_: str = field(default="")
    klass: set[str] = field(default_factory=set)
    tag: str = field(default="")

    def update_by_mode(self, mode: Mode, chars: list[str]) -> None:
        if len(chars) == 0:
            return

        value = "".join(chars)
        chars.clear()
        match mode:
            case Mode.ID:
                self.id_ = value
            case Mode.CLASS:
                self.klass.add(value)
            case Mode.TAG:
                self.tag = value

    @classmethod
    def from_str(cls, selector: str) -> Self:
        sel = cls()
        mode: Mode = Mode.TAG
        chars: list[str] = []
        for ch in selector:
            if ch == ".":
                sel.update_by_mode(mode, chars)
                mode = Mode.CLASS
                continue
            elif ch == "#":
                sel.update_by_mode(mode, chars)
                mode = Mode.ID
                continue

            chars.append(ch)

        sel.update_by_mode(mode, chars)
        logger.warning("Built selector: %s", sel)
        return sel

    def match_node(self, node: Node) -> bool:
        matched_tag = True
        if self.tag and self.tag != node.tag:
            matched_tag = False

        matched_id = True
        id_ = node.attributes.get("id")
        if self.id_ and self.id_ != id_:
            matched_id = False

        matched_class = True
        classes = node.attributes.get("class", "").split(" ")
        class_set = set([
            cs
            for cs in map(str.strip, classes)
            if cs
        ])
        if len(self.klass) and not self.klass.issubset(class_set):
            matched_class = False
        final = matched_tag and matched_id and matched_class
        if final:
            logger.warning(
                "Matched node [%s] tag=%s id=%s cls=%s",
                node,
                matched_tag,
                matched_id,
                matched_class,
            )
        return final

@dataclass
class Selectors:
    items: list[Selector]

    @classmethod
    def from_str(cls, selectors_str: str) -> Self:
        selectors = selectors_str.split(",")
        return cls([
            Selector.from_str(sel)
            for sel in map(str.strip, selectors)
        ])

    def match_node(self, node: Node) -> bool:
        return any(
            sel.match_node(node)
            for sel in self.items
        )

def verify_node(
    node: Node,
    selector: Selectors,
    *,
    matched: list[Node],
) -> None:
    if selector.match_node(node):
        matched.append(node)

    for child in node.children:
        verify_node(child, selector, matched=matched)

def query_selector_all(node: Node, selector: str) -> list[Node]:
    """
    Given a node, the function will return all nodes, including children,
    that match the given selector.
    """
    matched_nodes: list[Node] = []
    verify_node(
        node,
        Selectors.from_str(selector),
        matched=matched_nodes,
    )
    logger.warning("Matched [%d] nodes", len(matched_nodes))
    return matched_nodes
