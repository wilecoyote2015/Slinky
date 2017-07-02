#!/usr/bin/env python

# These two lines are only needed if you don't put the script directly into
# the installation directory
import sys
import os
import tempfile
import shutil
import subprocess

# We will use the inkex module with the predefined Effect base class.
import inkex
# The simplestyle module provides functions for style parsing.
from simplestyle import *

# todo: export layers as single pdfs first and then merge them if this is possible. Is there a python lib for that?

class HelloWorldEffect(inkex.Effect):
    """
    Example Inkscape effect extension.
    Creates a new layer with a "Hello World!" text centered in the middle of the document.
    """
    def __init__(self):
        """
        Constructor.
        Defines the "--what" option of a script.
        """
        # Call the base class constructor.
        inkex.Effect.__init__(self)

        # Define string option "--what" with "-w" shortcut and default value "World".
        self.OptionParser.add_option('-b', '--Background', action = 'store',
          type = 'string', dest = 'background_layer', default = '',
          help = 'Name of background layer')

        self.OptionParser.add_option('-t', '--TitleSlide', action = 'store',
          type = 'string', dest = 'title_layer', default = '',
          help = 'Name of title slide layer')

        self.OptionParser.add_option('-o', '--OutputDirectory', action = 'store',
          type = 'string', dest = 'output_directory', default = '',
          help = 'Full path to directory where individual pdf slides will be saved')

        self.top_layers = None

    def effect(self):
        # """
        # Effect behaviour.
        # Overrides base class' method and inserts "Hello World" text into SVG document.
        # """
        # # Get script's "--what" option value.
        # what = self.options.what
        #
        # # Get access to main SVG document element and get its dimensions.
        # svg = self.document.getroot()
        # # or alternatively
        # # svg = self.document.xpath('//svg:svg',namespaces=inkex.NSS)[0]
        #
        # # Again, there are two ways to get the attibutes:
        # width  = self.unittouu(svg.get('width'))
        # height = self.unittouu(svg.attrib['height'])
        #
        # # Create a new layer.
        # layer = inkex.etree.SubElement(svg, 'g')
        # layer.set(inkex.addNS('label', 'inkscape'), 'Hello %s Layer' % (what))
        # layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')
        #
        # # Create text element
        # text = inkex.etree.Element(inkex.addNS('text','svg'))
        # text.text = 'Hello %s!' % (what)
        #
        # # Set text position to center of document.
        # text.set('x', str(width / 2))
        # text.set('y', str(height / 2))
        #
        # # Center text horizontally with CSS style.
        # style = {'text-align' : 'center', 'text-anchor': 'middle'}
        # text.set('style', formatStyle(style))
        #
        # # Connect elements together.
        # layer.append(text)

        if not os.path.dirname(self.options.output_directory):
            inkex.errormsg(_('Please provide a valid output directory.'))
            exit()

        self.top_layers = self.get_all_top_layers()
        slide_layers = self.get_slide_layers()

        for index_slide_layer in range(len(slide_layers)):
            slide_layer = slide_layers[index_slide_layer]
            self.export_slide_layer(slide_layer, index_slide_layer)

        title_layer = self.get_top_layer_by_name(self.options.title_layer)
        if title_layer is not None:
            self.export_slide_layer(title_layer, -1, show_background=False)

    def get_all_top_layers(self):
        svg = self.document.getroot()
        return self.get_all_subelements_of_element(svg, "g", "svg")

    def get_slide_layers(self):
        slide_layers = []
        for layer in self.top_layers:
            label = layer.get("{" + inkex.NSS["inkscape"] + "}label")
            if label != self.options.background_layer and label != self.options.title_layer:
                slide_layers.append(layer)

        return slide_layers

    def get_top_layer_by_name(self, layer_name):
        for layer in self.top_layers:
            label = layer.get("{" + inkex.NSS["inkscape"] + "}label")
            if label == layer_name:
                return layer
        return None

    def export_slide_layer(self, slide_layer, index_slide_layer, show_background=True):
        self.hide_all_top_layers_except_current_slide(slide_layer, show_background=show_background)

        # set the slide number
        slide_number = index_slide_layer + 1
        background_layer = self.get_top_layer_by_name(self.options.background_layer)
        self.set_slide_number_in_layer(slide_layer, slide_number)
        if background_layer is not None:
            self.set_slide_number_in_layer(background_layer, slide_number)

        filename = str(slide_number) + ".pdf"
        output_path = os.path.join(self.options.output_directory, filename)
        self.save_document_as_pdf(output_path)

        # reset slide number strings
        self.reset_slide_number_text(slide_layer)
        if background_layer is not None:
            self.reset_slide_number_text(background_layer)

    def hide_all_top_layers_except_current_slide(self, current_slide, show_background=True):
        self.hide_all_top_layers()
        if show_background:
            self.unhide_background_layer()

        self.unhide_layer(current_slide)

    def hide_all_top_layers(self):
        for layer in self.top_layers:
            self.hide_layer(layer)

    def unhide_background_layer(self):
        # get background layer
        background_layer = self.get_top_layer_by_name(self.options.background_layer)

        # unide background layer
        if background_layer is not None:
            self.unhide_layer(background_layer)

    def unhide_layer(self, layer):
        # todo: correct that way?
        layer.attrib.pop("style")


    def hide_layer(self, layer):
        layer.set("style", "display:none")
        pass

    def get_all_subelements_of_element(self, element, subelement_name, namespace=None):
        # todo: make this work?
        if namespace is not None:
            path = namespace + ":" + subelement_name
        else:
            path = subelement_name
        return element.findall(path, namespaces=inkex.NSS)

    def set_slide_number_in_layer(self, slide_layer, slide_number):
        for tspan in slide_layer.iter("{" + inkex.NSS["svg"] + "}tspan"):
            tspan.text = str(slide_number)
            tspan.set("slidenumber", str(slide_number))

    def reset_slide_number_text(self, slide_layer):
        for tspan in slide_layer.iter("{" + inkex.NSS["svg"] + "}tspan"):
            if "slidenumber" in tspan.attrib:
                tspan.text = "$sn"
                tspan.attrib.pop("slidenumber")


    def save_document_as_pdf(self, output_filepath):
        # create temporary directory
        #temp_directory = tempfile.mkdtemp()
        temp_descriptor, temp_filepath = tempfile.mkstemp(suffix=".svg", text=True)
        temp_file = open(temp_filepath, 'w')



        # save the current svg to it
        xml_string = inkex.etree.tostring(self.document)
        temp_file.write(xml_string)
        temp_file.close()

        # open an inkscape process to save the document as pdf
        command = "inkscape --export-pdf=\"{}\" {}".format(output_filepath, temp_filepath)

        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return_code = p.wait()
        f = p.stdout
        err = p.stderr
        # todo: debug message if something failes

        # delete the temp directory
        #shutil.rmtree(temp_directory)
        os.close(temp_descriptor)
        os.remove(temp_filepath)

# Create effect instance and apply it.
effect = HelloWorldEffect()
effect.affect()