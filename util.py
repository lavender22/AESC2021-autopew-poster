from PIL import Image as PImage
from IPython.display import display
from ipywidgets.widgets import Image
import numpy as np


def backup_pick_samples(imagepath):
    with open("./Supplementary Material/GUI_samples.gif", "rb") as file:
        data = file.read()
    im = Image(value=data, width="70%", format="gif")
    display(im)
    points = np.array([[ 554.61220444,101.90381528],
                       [ 677.21147261,110.07709983],
                         [ 639.9776208,140.04580982],
                         [ 802.53516896,169.10637709],
                         [ 677.21147261,111.89338528],
                         [ 769.84203078,271.72650526],
                         [ 939.66472076,193.62623073],
                         [ 939.66472076,238.12522436],
                         [ 774.38274442,530.5471825 ],
                         [ 452.900219,404.31534343],
                         [ 520.10278081,640.43245249],
                         [ 260.37396085,518.74132705],
                         [ 339.38237811,570.5054625 ],
                         [ 382.06508629,807.53071428],
                         [ 695.37432715,876.54956155],
                         [ 744.41403442,921.04855518],
                         [ 830.6875935,841.13199519],
                         [ 926.04257985,825.69356883],
                         [ 852.48301895,773.02129065],
                         [ 843.40159168,711.26758521],
                         [ 793.45374169,658.59530703],
                         [1291.11595617,983.71040335],
                         [1263.87167435,1053.63739334],
                         [1378.29765798,1069.0758197 ],
                         [1447.31650524,939.21140972],
                         [1447.31650524,984.61854608],
                         [1410.99079615,879.27398973],
                         [1462.7549316,859.29484973],
                         [1154.89454709,786.64343156],
                         [1013.22428166,308.96035708],
                         [1149.44569073,226.3193689 ],
                         [1332.89052162,356.18377889],
                         [1345.6045198,336.20463889],
                         [1363.76737434,541.44489523],
                         [1418.25593797,576.86246159],
                         [1427.33736524,571.41360522],
                         [1600.79262613,567.78103431],
                         [1597.16005522,488.77261705],
                         [1645.29161976,446.08990888],
                         [1722.48375157,338.92906707],
                         [1748.81989065,301.69521526],
                         [1772.43160156,226.3193689 ],
                         [1803.30845428,274.45093344],
                         [1838.72602064,360.72449252],
                         [1924.99957972,419.75376979],
                         [1883.22501427,556.88332159],
                         [1732.47332157,641.34059521],
                         [1700.68832612,723.98158339],
                         [1768.79903065,760.30729247],
                         [1796.04331247,727.61415429],
                         [2048.50699062,659.50344976],
                         [2037.60927789,668.58487703],
                         [1987.6614279,636.79988158],
                         [2032.16042153,908.334557,],
                         [2100.27112606,1067.25953425],
                         [1930.44843609,1058.17810698],
                         [2353.64294694,921.04855518],
                         [2343.65337694,792.09228792],
                         [2335.4800924,687.6558743 ],
                         [2172.92254424,563.24032068],
                         [2241.9413915,268.09393435],
                         [2262.82867422,274.45093344],
                         [2018.53828062,180.91223255],
                         [2318.22538058,202.707658,]])
    return points

def backup_pick_calibration_points(imagepath):
    with open("./Supplementary Material/GUI_calibration.gif", "rb") as file:
        data = file.read()
    im = Image(value=data, width="70%", format="gif")
    display(im)
    points= np.array([[ 788.6398347 ,  552.35486037],
                      [1919.31460625, 1062.41913351],
                      [1722.24763446,  661.92819084],
                      [2008.31259351,  172.4392609 ]])
    return points


def resize_gif(path, save_as=None, resize_to=None):
    """
    Resizes the GIF to a given length:

    Args:
        path: the path to the GIF file
        save_as (optional): Path of the resized gif. If not set, the original gif will be overwritten.
        resize_to (optional): new size of the gif. Format: (int, int). If not set, the original GIF will be resized to
                              half of its size.
    """
    all_frames = extract_and_resize_frames(path, resize_to)

    if not save_as:
        save_as = path

    if len(all_frames) == 1:
        print("Warning: only 1 frame found")
        all_frames[0].save(save_as, optimize=True)
    else:
        all_frames[0].save(
            save_as,
            optimize=True,
            save_all=True,
            append_images=all_frames[1:],
            loop=1000,
        )


def analyseImage(path):
    """
    Pre-process pass over the image to determine the mode (full or additive).
    Necessary as assessing single frames isn't reliable. Need to know the mode
    before processing all frames.
    """
    im = PImage.open(path)
    results = {
        "size": im.size,
        "mode": "full",
    }
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results["mode"] = "partial"
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return results


def extract_and_resize_frames(path, resize_to=None):
    """
    Iterate the GIF, extracting each frame and resizing them

    Returns:
        An array of all frames
    """
    mode = analyseImage(path)["mode"]

    im = PImage.open(path)

    if not resize_to:
        resize_to = (im.size[0] // 2, im.size[1] // 2)

    i = 0
    p = im.getpalette()
    last_frame = im.convert("RGBA")

    all_frames = []

    try:
        while True:
            # print("saving %s (%s) frame %d, %s %s" % (path, mode, i, im.size, im.tile))

            """
            If the GIF uses local colour tables, each frame will have its own palette.
            If not, we need to apply the global palette to the new frame.
            """
            if not im.getpalette():
                im.putpalette(p)

            new_frame = PImage.new("RGBA", im.size)

            """
            Is this file a "partial"-mode GIF where frames update a region of a different size to the entire image?
            If so, we need to construct the new frame by pasting it on top of the preceding frames.
            """
            if mode == "partial":
                new_frame.paste(last_frame)

            new_frame.paste(im, (0, 0), im.convert("RGBA"))

            new_frame.thumbnail(resize_to, PImage.ANTIALIAS)
            all_frames.append(new_frame)

            i += 1
            last_frame = new_frame
            im.seek(im.tell() + 1)
    except EOFError:
        pass

    return all_frames
