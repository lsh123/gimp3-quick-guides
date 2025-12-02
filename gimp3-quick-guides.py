#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gtk
import sys

plug_in_proc   = "gimp3-quick-guides"
plug_in_binary = "py3-gimp3-quick-guides"


class Gimp3QuickGuides (Gimp.PlugIn):
  def do_query_procedures(self):
    return [ plug_in_proc ]

  def parse_guide_string(self, guide_str):
    """Parse comma-separated guide positions into a list of integers.

    Args:
      guide_str: String with comma-separated positions (e.g., "10,20,30")

    Returns:
      List of integer positions, sorted and deduplicated
    """
    if not guide_str or guide_str.strip() == "":
      return []

    positions = []
    for pos in guide_str.split(','):
      pos = pos.strip()
      if pos:
        try:
          positions.append(int(pos))
        except ValueError:
          Gimp.message(f"Warning: Invalid guide position '{pos}', skipping")

    # Remove duplicates and sort
    return sorted(set(positions))

  def find_guide_changes(self, current_positions, new_positions):
    """Find additions and deletions between current and new guide positions.

    Args:
      current_positions: List of current guide positions
      new_positions: List of desired guide positions

    Returns:
      Tuple of (additions, deletions) where each is a list of positions
    """
    current_set = set(current_positions)
    new_set = set(new_positions)

    additions = sorted(new_set - current_set)
    deletions = sorted(current_set - new_set)

    return (additions, deletions)

  def get_guides(self, image):
    """Get all guides from the image organized by orientation.

    Returns:
      dict: Dictionary with 'horizontal' and 'vertical' keys containing lists of guide positions
    """

    guides_dict = {
      'horizontal': [],
      'vertical': []
    }

    # Get all guides from the image using find_next_guide
    guide = image.find_next_guide(0)
    while guide is not None and guide != 0:
      orientation = image.get_guide_orientation(guide)
      position = image.get_guide_position(guide)

      if orientation == Gimp.OrientationType.HORIZONTAL:
        guides_dict['horizontal'].append(position)
      elif orientation == Gimp.OrientationType.VERTICAL:
        guides_dict['vertical'].append(position)

      guide = image.find_next_guide(guide)

    guides_dict['vertical'].sort()
    guides_dict['horizontal'].sort()
    return guides_dict

  def find_guide_id(self, image, position, orientation):
    """Find guide ID for a guide at the specified position and orientation.

    Args:
      image: The GIMP image
      position: Integer position of the guide
      orientation: Gimp.OrientationType (HORIZONTAL or VERTICAL)

    Returns:
      Guide ID if found, None otherwise
    """
    # Iterate through all guides using find_next_guide
    guide = image.find_next_guide(0)
    while guide is not None and guide != 0:
      guide_orientation = image.get_guide_orientation(guide)
      guide_position = image.get_guide_position(guide)

      if guide_orientation == orientation and guide_position == position:
        return guide

      guide = image.find_next_guide(guide)

    return None

  def delete_guides(self, image, orientation, positions):
    """Delete guides from the image at specified positions and orientation.

    Args:
      image: The GIMP image
      orientation: Gimp.OrientationType (HORIZONTAL or VERTICAL)
      positions: List of integer positions to delete
    """
    for pos in positions:
      guide_id = self.find_guide_id(image, pos, orientation)
      if guide_id is not None:
        image.delete_guide(guide_id)
        Gimp.message(f"Gimp3QuickGuides: Deleted guide at position {pos} ({'HORIZONTAL' if orientation == Gimp.OrientationType.HORIZONTAL else 'VERTICAL'})")
      else:
        Gimp.message(f"Gimp3QuickGuides: No guide found at position {pos} to delete")

  def add_guides(self, image, orientation, positions):
    """Add guides to the image at specified positions and orientation.
    Args:
      image: The GIMP image
      orientation: Gimp.OrientationType (HORIZONTAL or VERTICAL)
      positions: List of integer positions to add
    """
    for pos in positions:
      if orientation == Gimp.OrientationType.HORIZONTAL:
        image.add_hguide(pos)
      else:
        image.add_vguide(pos)
      Gimp.message(f"Gimp3QuickGuides: Added guide at position {pos} ({'HORIZONTAL' if orientation == Gimp.OrientationType.HORIZONTAL else 'VERTICAL'})")

  def run(self, procedure, run_mode, image, drawables, config, run_data):
    if image is None:
      return procedure.new_return_values (Gimp.PDBStatusType.CALLING_ERROR,
                                          GLib.Error(f"Procedure '{plug_in_proc}' requires an image."))
    Gimp.message("Gimp3QuickGuides: started")

    # get current guides
    cur_guides = self.get_guides(image)

    # interactive mode
    if run_mode == Gimp.RunMode.INTERACTIVE:
      GimpUi.init(plug_in_binary)

      # set current guides as default values
      h_guides = ",".join(map(str, cur_guides['horizontal']))
      config.set_property('h_guides', h_guides)

      v_guides = ",".join(map(str, cur_guides['vertical']))
      config.set_property('v_guides', v_guides)

      # run dialog
      dialog = GimpUi.ProcedureDialog.new(procedure, config, "Quick Guides")
      dialog.fill(None)
      if not dialog.run():
        dialog.destroy()
        return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)
      else:
        dialog.destroy()

    # get new guides from config (after dialog or non-interactive run)
    new_h_guides = config.get_property('h_guides')
    new_v_guides = config.get_property('v_guides')

    # parse guides
    new_h_positions = self.parse_guide_string(new_h_guides)
    new_v_positions = self.parse_guide_string(new_v_guides)

    # find what needs to be added/deleted
    h_additions, h_deletions = self.find_guide_changes(cur_guides['horizontal'], new_h_positions)
    v_additions, v_deletions = self.find_guide_changes(cur_guides['vertical'], new_v_positions)

    # apply changes
    image.undo_group_start()
    self.add_guides(image, Gimp.OrientationType.HORIZONTAL, h_additions)
    self.delete_guides(image, Gimp.OrientationType.HORIZONTAL, h_deletions)
    self.add_guides(image, Gimp.OrientationType.VERTICAL, v_additions)
    self.delete_guides(image, Gimp.OrientationType.VERTICAL, v_deletions)
    image.undo_group_end()

    # done, return:
    Gimp.message("Gimp3QuickGuides: finished")
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


  def do_create_procedure(self, name):
    procedure = None

    if name == plug_in_proc:
      procedure = Gimp.ImageProcedure.new(self, name,
                                          Gimp.PDBProcType.PLUGIN,
                                          self.run, None)
      procedure.set_image_types("*")
      procedure.set_sensitivity_mask (Gimp.ProcedureSensitivityMask.DRAWABLE |
                                      Gimp.ProcedureSensitivityMask.NO_DRAWABLES)
      procedure.set_menu_label("Quick _Guides")
      procedure.add_menu_path ("<Image>/_Aleksey Plugins")

      procedure.set_attribution("Alekjsey", "Aleksey", "2025")
      procedure.set_documentation ("Quick guides configuration", None)

      procedure.add_string_argument  ("h_guides", "Horizontal guides (comma separated):", None, "", GObject.ParamFlags.READWRITE)
      procedure.add_string_argument  ("v_guides", "Vertical guides (comma separated):", None, "", GObject.ParamFlags.READWRITE)

    return procedure

Gimp.main(Gimp3QuickGuides.__gtype__, sys.argv)
