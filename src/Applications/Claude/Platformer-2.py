            + [('P', c, 10) for c in range(11, 15)]
            + [('P', c, 7) for c in range(15, 19)]
            + [('P', c, 4) for c in range(20, 24)]
            + [('P', c, 7) for c in range(25, 29)]
            + [('P', c, 10) for c in range(30, 34)]
            + [('G', c, 13) for c in range(35, 43)]
            + [('G', c, 14) for c in range(35, 43)]
        ),
        "coins": [
            (4, 12), (8, 12),
            (12, 9), (13, 9),
            (16, 6), (17, 6), (18, 6),
            (21, 3), (22, 3), (23, 3),
            (26, 6), (27, 6),
            (31, 9), (32, 9),
            (37, 12), (40, 12),
        ],
        "boxes": [(6, 12), (36, 12)],
        "door": (41, 12),
        "spawn": (1, 12),
    },

    # ── Level 8: Snowdrift Switchbacks ───────────────────────────────────────
    {
        "name": "Snowdrift Switchbacks",
        "bg_color": (185, 225, 245),
        "tiles": (
            [('G', c, 13) for c in range(0, 12)]
            + [('G', c, 14) for c in range(0, 12)]
            + [('P', c, 10) for c in range(4, 9)]
            + [('P', c, 8) for c in range(11, 16)]
            + [('P', c, 6) for c in range(6, 11)]
            + [('P', c, 4) for c in range(14, 19)]
            + [('P', c, 7) for c in range(20, 25)]
            + [('P', c, 10) for c in range(25, 30)]
            + [('G', c, 13) for c in range(31, 39)]
            + [('G', c, 14) for c in range(31, 39)]
        ),
        "coins": [
            (5, 9), (7, 9),
            (8, 5), (9, 5), (10, 5),
            (12, 7), (14, 7),
            (15, 3), (16, 3), (17, 3),
            (21, 6), (23, 6),
            (26, 9), (28, 9),
            (34, 12), (36, 12),
        ],
        "boxes": [(2, 12), (12, 12), (32, 12)],
        "door": (37, 12),
        "spawn": (1, 12),
    },

    # ── Level 9: Moonlit Floes ───────────────────────────────────────────────
    {
        "name": "Moonlit Floes",
        "bg_color": (80, 120, 180),
        "tiles": (
            [('G', c, 13) for c in range(0, 5)]
            + [('G', c, 14) for c in range(0, 5)]
            + [('P', c, 11) for c in range(6, 9)]
            + [('P', c, 9) for c in range(10, 13)]
            + [('P', c, 7) for c in range(14, 17)]
            + [('P', c, 5) for c in range(18, 22)]
            + [('P', c, 8) for c in range(23, 26)]
            + [('P', c, 11) for c in range(27, 31)]
            + [('P', c, 8) for c in range(32, 36)]
            + [('G', c, 13) for c in range(38, 45)]
            + [('G', c, 14) for c in range(38, 45)]
        ),
        "coins": [
            (2, 12),
            (7, 10), (8, 10),
            (11, 8), (12, 8),
            (15, 6), (16, 6),
            (19, 4), (20, 4), (21, 4),
            (24, 7), (25, 7),
            (28, 10), (29, 10),
            (33, 7), (34, 7), (35, 7),
            (40, 12), (43, 12),
        ],
        "boxes": [(3, 12), (28, 10), (39, 12)],
        "door": (43, 12),
        "spawn": (1, 12),
    },

    # ── Level 10: Emperor's Ascent ───────────────────────────────────────────
    {
        "name": "Emperor's Ascent",
        "bg_color": (105, 170, 215),
        "tiles": (
            [('G', c, 13) for c in range(0, 9)]
            + [('G', c, 14) for c in range(0, 9)]
            + [('P', c, 11) for c in range(9, 13)]
            + [('P', c, 9) for c in range(13, 17)]
            + [('P', c, 7) for c in range(17, 21)]
            + [('P', c, 5) for c in range(21, 25)]
            + [('P', c, 8) for c in range(26, 30)]
            + [('P', c, 10) for c in range(31, 35)]
            + [('P', c, 7) for c in range(36, 40)]
            + [('P', c, 4) for c in range(41, 46)]
            + [('G', c, 13) for c in range(47, 55)]
            + [('G', c, 14) for c in range(47, 55)]
        ),
        "coins": [
            (4, 12), (7, 12),
            (10, 10), (11, 10), (12, 10),
            (14, 8), (15, 8), (16, 8),
            (18, 6), (19, 6), (20, 6),
            (22, 4), (23, 4), (24, 4),
            (27, 7), (28, 7), (29, 7),
            (32, 9), (33, 9),
            (37, 6), (38, 6), (39, 6),
            (42, 3), (43, 3), (44, 3), (45, 3),
            (49, 12), (52, 12),
        ],
        "boxes": [(2, 12), (8, 12), (25, 12), (48, 12)],
        "door": (53, 12),
        "spawn": (1, 12),
    },
]




if __name__ == "__main__":
    main()
    main()