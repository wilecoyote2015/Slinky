# Slinky
Slinky is an Inkscape extension for the creation of presentation slides as PDF files.


# Usage
Your Inkscape document should be structured as described below (all without the parenthesis):
* One layer per slide with as many sublayers as you like.
* Optional: One layer named "Title", which will be the title slide. For this slide, the optionally defined Background is not visible in the exported pdf.
* Optionally: One layer at the botton of the layer stack named "Background", which contains the background shown on all slides except the title slide.
* You may insert the slide number by creating a text that contains only "$sn". On export, this will be replaced by the slide numbers.
    This can also be used on the background slide.
    
Then, use the Slinky extension from the extensions menu in order to export your presentation slides as individual pdf files automatically. If you like to use different names for the title an background layers, you may specify this. 
Enter the Full path to the directory where the slides shall be exported and apply the extension.
