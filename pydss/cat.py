""" Cat Module
    Class-based representation of the Cat smart contract
    (contains only what is necessary for the simulation)
"""

from pydss.pymaker.numeric import Wad, Rad, Ray
from pydss.util import require


class Ilk:
    """
    id = str
    flip = Flipper
    chop = Wad
    dunk = Rad
    """

    def __init__(self, ilk_id):
        self.id = ilk_id
        self.chop = Wad(0)
        self.dunk = Rad(0)


class Cat:
    """
    ADDRESS = str

    ilks = dict[str: Ilk]

    vat = Vat
    vow = Vow
    box = Rad
    litter = Rad
    """

    def __init__(self, vat):
        self.ADDRESS = "cat"
        self.ilks = {}
        self.vat = vat
        self.box = Rad(0)
        self.litter = Rad(0)
        self.vow = None

    def file(self, what, data):
        # TODO: Typechecking here?
        if what == "vow":
            self.vow = data
        elif what == "box":
            self.box = data
        else:
            # TODO: Custom exception classes?
            raise Exception("Cat/file-unrecognized-param")

    def file_ilk(self, ilk_id, what, data):
        if what in ("chop", "dunk", "flip"):
            if not self.ilks.get(ilk_id):
                self.ilks[ilk_id] = Ilk(ilk_id)
            if what == "chop":
                self.ilks[ilk_id].chop = data
            elif what == "dunk":
                self.ilks[ilk_id].dunk = data
            elif what == "flip":
                # TODO: nope-ing & hope-ing here
                self.ilks[ilk_id].flip = data

    def bite(self, ilk_id, urn, now):
        # TODO: Remove `now` once better timekeeping solution is implemented

        rate = self.vat.ilks[ilk_id].rate
        spot = self.vat.ilks[ilk_id].spot
        dust = self.vat.ilks[ilk_id].dust
        ink = self.vat.urns[ilk_id][urn].ink
        art = self.vat.urns[ilk_id][urn].art

        require(spot > Ray(0) and Rad(ink * spot) < Rad(art * rate), "Cat/not-unsafe")

        milk = self.ilks[ilk_id]

        room = self.box - self.litter
        require(self.litter < self.box and room >= dust, "Cat/liquidation-limit-hit")

        dart = Wad.min(art, Wad(Rad.min(milk.dunk, room)) / Wad(rate) / milk.chop)
        dink = Wad.min(ink, ink * dart / art)

        require(dart > Wad(0) and dink > Wad(0), "Cat/null-auction")
        require(
            dart <= Wad.from_number(2 ** 255) and dink <= Wad.from_number(2 ** 255),
            "Cat/overflow",
        )

        self.vat.grab(
            ilk_id, urn, self.ADDRESS, self.vow.ADDRESS, Wad(0) - dink, Wad(0) - dart
        )
        self.vow.fess(Rad(dart * rate), now)

        tab = Rad(dart * rate * milk.chop)
        self.litter += tab

        milk.flip.kick(urn, self.vow.ADDRESS, tab, dink, Rad(0), now)

    def claw(self, rad):
        self.litter -= rad
