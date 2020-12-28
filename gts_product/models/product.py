from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tests import common, Form

tray1 = [15542, 15544, 15546, 15551, 15555, 15559, 15561, 15565, 15568, 15570, 15574, 15576, 15578, 18573, 15580, 18574, 15583, 18575, 15586, 15588, 15590, 15592, 15594, 15899, 15902, 15904, 18576, 18577, 14778, 14782, 14788, 14793, 21149, 21151, 21078, 20939, 20941, 20912, 21129, 21290, 20999, 21042, 20974, 18256, 14813, 14816, 14821, 14822, 14825, 14829, 14831, 14835, 18332, 18333, 14840, 18334, 14842, 14845, 14847, 14849, 14850, 18335, 14854, 14856, 14861, 14864, 14867, 14870, 14872, 14876, 14878, 14880, 14883, 14885, 14887, 14889, 14892, 14893, 14894, 14898, 14900, 14902, 14903, 14906, 14907, 14910, 14912, 14914, 14917, 14919, 14921, 14923, 14925, 14927, 14929, 14932, 14934, 14938, 14940, 14942, 14944, 14946, 14948, 14950, 14953, 14955, 14957, 14960, 14962, 14964, 14967, 14970, 14972, 14974, 14979, 14982, 14984, 14986, 14988, 18336, 14994, 14996, 14998, 15000, 15002, 15004, 15007, 15009, 15011, 15013, 15016, 15018, 15020, 15022, 15027, 15029, 15031, 15033, 15035, 15037, 15042, 15044, 15046, 15048, 15050, 15052, 15054, 15056, 15058, 15061, 15065, 15069, 15072, 15074, 15076, 15078, 15080, 15082, 15084, 15086, 15088, 15091, 15093, 15096, 15098, 15101, 15104, 15106, 15109, 15111, 15113, 15116, 15118, 18337, 18338, 18339, 18340, 18341, 18342, 18064, 18343, 18344, 18345, 18346, 20882, 20982, 20181, 16027, 21163, 21161, 15636, 15638, 15640, 15642, 15644, 15646, 18476, 15648, 15651, 15653, 18477, 15655, 15657, 15660, 15662, 15664, 18478, 18479, 18480, 18481, 17843, 17844, 17842, 18482, 20931, 20124, 20937, 20911, 21115, 21117, 21302, 21304, 20916, 15524, 15526, 18502, 18504, 20929, 20930, 20984, 21002, 15214, 20874, 15218, 15220, 18087, 15222, 15224, 15226, 15233, 15235, 15238, 15240, 15243, 15245, 15247, 20867, 15251, 15253, 15255, 15257, 20871, 15261, 18084, 15266, 15269, 15271, 15273, 18565, 15275, 15277, 18566, 17764, 18567, 18568, 17834, 18569, 16070, 18050, 17836, 18570, 17862, 18060, 20096, 20164, 20976, 21121, 15548, 562, 20168, 20989, 20972, 21094, 21134, 15279, 15281, 15283, 15285, 18598, 15288, 18599, 17872, 18600, 18601, 20079, 21131, 21136, 18797, 18798, 15306, 15309, 15312, 18799, 18800, 18801, 18802, 15314, 15317, 15319, 15321, 15323, 15325, 15327, 15329, 15331, 20952, 18803, 18804, 18805, 15333, 15336, 18806, 15338, 18807, 18808, 15340, 15342, 18809, 18810, 15344, 18811, 15346, 15348, 15350, 15352, 15354, 18812, 15356,18813, 15358, 15360, 15362, 15364, 15366, 15368, 15370, 18814, 15372, 15374, 18815, 15377, 18816, 15379, 15381, 18817, 15383,15385, 15387, 18818, 15389, 15391, 15394, 15906, 15908, 15910, 15912, 15914, 15916, 15918, 15920, 18819, 18820, 18821, 18822, 18098, 18823, 18824, 18825, 21159, 21119, 20143, 20880, 20942, 20979, 582, 20879, 20927, 20928, 580, 21019, 577, 16015, 20671, 20669, 21006, 21015, 21059]
tray2 = [21074, 21138, 21167, 21306, 15120, 15123, 18858, 15125, 564, 15131, 15133, 15136, 15138, 15140, 15142, 15144, 15146, 15148, 15150, 15152, 15154, 15157, 15159, 15161, 15163, 15165, 18859, 15168, 18860, 15170, 15172, 15174, 15177, 15179, 15181, 15183, 15185, 15187, 15189, 15192, 15194, 15196, 15198, 15201, 15203, 15205, 15207, 15209, 15211, 18861, 18862, 18863, 18864, 20090, 20873, 15290, 15292, 15295, 15297, 15299, 15301, 15303, 21070, 20876, 21040, 15689, 15691, 15693, 15695, 15697, 15699, 15701, 15703, 15705, 15708, 18875, 18876, 17595, 18877, 20944, 20943, 20945, 21056, 21107, 20961, 20970, 21017, 21025, 21052, 21099, 21101, 21104, 21126, 21155, 21157, 21757, 21127, 21080, 15596, 18899, 15598, 15600, 15602, 18900, 15604, 18901, 15606, 15608, 15611, 15957, 15614, 15616, 15618, 18902, 18903, 21061, 18947, 18948, 15678, 15680, 15682, 15684, 15686, 15710, 15712, 15714, 15717, 15719, 15721, 15723, 15725, 15727, 15729, 15731, 15734, 15736, 15738, 15740, 15742, 15744, 15748, 15750, 15752, 15754, 15756, 17838, 17839, 17837, 17833, 17840, 15668, 15671, 15676, 21308, 574, 570, 16018, 20957, 20959, 17847, 21141, 21143, 15771, 19895, 18070, 19896, 19897, 18080, 19898, 589, 15774, 15776, 19899, 15780, 15784, 15786, 17716, 21064, 19901, 19902, 19903, 19904, 16022, 19905, 19906, 19907, 19908, 19909, 17866, 17871, 19910, 21667, 19912, 18085, 19913, 19914, 15788, 19915, 17952, 19916, 19917, 19918, 19919, 19920, 19921, 19922, 19923, 19924, 19925, 19926, 19927, 19928, 19929, 19930, 19931, 19932, 19933, 18163, 19934, 19935, 19936, 590, 591, 16021, 19937, 15965, 19938, 15790, 19939, 19940, 17828, 17592, 19941, 19942, 19943, 19944, 19945, 19946, 19947, 19948, 19949, 19950, 19951, 15792, 19952, 15796, 15797, 15798, 15800, 15803, 15806, 18141, 15816, 19953, 592, 593, 19954, 15819, 15823, 15826, 15966, 15830, 15832, 15834, 15836, 15837, 15840, 15841, 15844, 15845, 15849, 15851, 15853, 15855, 19955, 15857, 19956, 15859, 19957, 15862, 15866, 19958, 19959, 19960, 19961, 19962, 19963, 19964, 19965, 19966, 19967, 19968, 19969, 19970, 19971, 19972, 15868, 19973, 19974, 19975, 19976, 19977, 19978, 19979, 19980, 19981, 19982, 19983, 15870, 17845, 19984, 19985, 19986, 19987, 19988, 17758, 19989, 16065, 15872, 19990, 19991, 19992, 19993, 594, 15877, 15880, 19994, 15882, 15884, 15887, 19995, 19996, 19997, 15891, 15893, 19998, 19999, 20000, 20002, 20003, 20004, 20005, 20006, 20007, 20008, 20009, 20010, 20011, 20012, 20013, 20014, 20015, 20016, 20017, 20881, 20987, 20955, 21044, 21054, 21072, 21086, 21088, 21090, 21092, 21294, 20145, 20142, 20146, 20144, 15897, 15396, 15398, 15403, 15405, 15407, 15412, 15415, 15417, 15419, 15422, 15424, 15426, 15428, 15431, 15433, 15435, 15437, 15439, 15441, 15444, 15446, 15448, 15450, 15452, 15454, 15457, 15460, 15462, 15464, 15466, 15468, 15471, 15473, 15475, 15477, 15479, 15481, 15483, 15485, 15487, 15489, 15491, 15493, 15495, 15498, 15500, 15502, 15504, 15508, 20060, 20061, 20062, 20063, 20064, 20065, 20066, 20067, 20068, 20069, 20668, 21066, 21297, 21076, 21084, 18505, 18506, 20177, 21082, 21096, 21123, 20001, 17985, 16017]
prods = [14776, 14786, 14787, 14794, 20595, 20530, 20551, 20526, 20836, 20584, 21077, 20938, 20940, 20935, 21128, 20566, 20577, 20591, 20598, 20621, 20998, 21041, 14795, 14804, 14805, 14809, 20537, 20973, 20567, 20568, 15619, 15621, 15623, 15625, 15963, 15964, 15628, 15631, 15633, 15763, 15764, 15765, 15766, 14812, 18198, 14815, 14820, 14823, 14824, 14828, 14833, 14834, 18243, 18244, 14839, 18245, 14841, 14844, 14848, 14851, 14852, 18246, 14853, 14859, 14862, 14863, 14866, 14869, 14871, 14875, 14877, 14879, 14882, 14884, 14886, 14888, 14891, 14895, 14896, 14897, 14899, 14901, 14904, 14905, 14908, 14909, 14911, 14913, 14916, 14918, 14920, 14922, 14924, 14926, 14928, 14931, 14933, 14937, 14939, 14941, 14943, 14945, 14947, 14949, 14952, 14954, 14956, 14959, 14961, 14963, 14966, 14969, 14971, 14973, 14978, 14981, 14983, 14985, 14987, 14990, 14993, 14995, 14997, 14999, 15001, 15003, 15006, 15008, 15010, 15012, 15015, 15017, 15019, 15021, 15026, 15028, 15030, 15032, 15034, 15036, 15041, 15043, 15045, 15047, 15049, 15051, 15053, 15055, 15057, 15060, 15064, 15068, 15071, 15073, 15075, 15077, 15079, 15081, 15083, 15085, 15087, 15090, 15092, 15094, 15097, 15100, 15103, 15105, 15108, 15110, 15112, 15115, 15117, 18002, 18247, 18248, 18249, 18250, 18251, 18063, 18252, 18253, 18254, 18255, 18186, 20837, 20531, 20539, 20562, 20549, 20838, 20594, 20839, 20840, 20540, 20841, 20605, 20624, 20604, 20632, 20634, 17558, 20996, 21012, 21022, 21029, 21075, 21083, 21162, 21160, 15635, 15637, 15639, 15641, 15643, 15645, 18365, 15647, 15650, 15652, 18366, 15654, 15656, 15658, 15659, 15661, 15663, 18367, 18368, 18369, 17928, 17922, 17927, 18370, 21009, 20123, 20536, 20558, 20607, 20932, 21114, 21116, 21301, 21303, 20915, 18495, 15509, 15511, 15978, 15513, 15517, 15519, 15521, 15523, 15525, 15527, 18532, 15530, 15532, 15534, 15536, 15538, 15540, 18533, 20636, 17982, 18498, 18029, 18152, 18151, 20842, 20843, 20844, 20579, 20845, 20846, 20589, 20586, 20981, 20963, 20983, 21001, 15213, 15215, 15217, 17860, 18150, 15221, 15223, 15225, 15232, 15234, 15237, 15239, 17910, 15244, 15246, 15248, 15250, 15252, 15254, 15256, 15258, 15260, 15263, 15265, 15268, 15270, 15272, 18562, 15274, 15276, 18017, 17763, 18019, 18016, 17851, 18563, 18052, 18068, 18051, 18564, 17823, 18059, 20095, 20847, 20848, 20556, 20557, 20891, 20975, 21120, 15541, 15543, 15545, 15547, 15550, 15552, 15554, 15558, 15560, 15564, 15567, 15569, 15573, 15575, 15577, 18571, 15579, 15581, 15582, 15584, 15585, 15587, 15589, 15591, 15593, 15898, 15901, 15903, 18009, 18572, 20534, 20573, 20866, 20528, 20581, 20583, 20631, 20849, 20971, 21093, 21133, 20619, 21037, 15278, 15280, 15282, 15284, 18594, 15287, 18595, 17929, 18596, 18597, 20078, 20850, 20851, 20852, 20572, 20548, 20853, 20533, 21130, 21135, 18770, 18771, 15305, 15308, 15311, 18772, 18773, 18774, 18775, 15313, 15316, 15318, 15320, 15322, 15324, 15326, 15328, 18099, 18061, 18776, 18777, 18778, 15332, 15335, 18779, 15337, 18155, 18780, 15339, 15341, 18781, 18782, 15343, 18783, 15345, 18171, 15349, 15351, 15353, 18784, 15355, 18785, 15357, 15359, 15361, 15363, 15365, 15367, 15369, 18786, 15371, 15373, 18787, 15376, 18788, 15378, 15380, 18789, 15382, 15384, 15386, 18790, 15388, 15390, 15393, 15905, 15907, 15909, 15911, 15913, 15915, 15917, 15919, 18791, 17959, 18792, 18793, 18172, 18794, 18795, 18796, 20854, 20855, 20856, 20857, 20858, 20859, 20580, 20582, 21118, 20917, 20535, 20559, 20596, 20622, 20592, 20620, 20555, 20599, 20603, 20641, 20643, 20644, 20645, 20646, 20968, 20936, 17453, 20908, 20907, 20980, 17449, 17532, 21018, 21020, 21005, 21007, 21014, 21026, 21027, 21035, 21058, 21073, 21081, 21095, 21137, 21166, 21305, 15119, 15122, 18852, 15124, 15126, 15130, 15132, 15135, 15137, 15139, 15141, 15143, 15145, 15147, 15149, 15151, 15153, 15156, 15158, 15160, 15162, 15164, 18853, 15167, 18854, 15169, 15171, 15173, 15176, 15178, 15180, 15182, 15184, 15186, 15188, 15191, 15193, 15195, 15197, 15200, 15202, 15204, 15206, 15208, 15210, 18855, 18031, 18856, 18857, 20091, 20550, 20563, 20877, 15289, 15291, 15294, 15296, 15298, 15300, 15302, 21069, 20611, 21039, 20612, 20613, 21122, 15688, 15690, 15692, 15694, 15696, 15698, 15700, 15702, 15704, 15707, 18001, 18887, 17896, 18888, 20524, 20525, 20561, 20618, 20946, 20948, 21055, 21106, 20960, 20969, 21016, 21024, 21051, 21098, 21100, 21103, 21125, 21154, 21156, 21756, 17733, 20627, 21079, 15595, 18922, 15597, 15599, 15601, 18923, 15603, 18924, 15605, 15607, 18925, 15613, 15960, 15615, 15617, 18926, 18927, 20560, 21060, 20527, 18945, 18946, 15677, 15679, 15681, 15683, 15685, 15709, 15711, 15713, 15716, 15718, 15720, 15722, 15724, 15726, 15728, 15730, 15733, 15735, 15737, 15739, 15741, 15743, 15747, 15749, 15751, 15753, 15755, 17899, 17900, 17897, 17902, 17903, 20538, 15667, 15670, 15675, 21307, 20956, 20933, 20924, 20925, 20958, 21140, 21142, 15770, 18049, 18038, 19185, 19186, 18149, 19187, 15772, 15773, 15775, 15782, 19189, 15783, 15785, 17857, 21063, 19191, 19192, 19193, 17911, 17932, 19194, 17979, 19195, 19196, 19197, 17919, 17945, 18035, 21666, 19199, 18036, 19200, 19201, 15807, 19202, 18065, 19203, 19204, 19205, 19206, 19207, 19208, 19209, 19210, 18012, 19211, 19212, 19213, 19214, 19215, 19216, 19217, 19218, 19219, 18162, 17864, 19220, 19221, 15808, 15809, 17965, 21031, 19222, 15789, 19223, 15810, 19224, 17865, 17891, 17880, 19225, 17962, 19226, 19227, 19228, 19229, 19230, 19231, 19232, 19233, 19234, 15791, 15811, 15795, 15812, 15802, 15813, 15801, 18157, 15814, 15815, 19236, 15817, 15818, 17855, 19237, 15824, 15827, 15828, 15829, 15831, 15833, 15835, 15838, 15839, 15842, 15843, 15847, 15848, 15850, 15852, 15854, 19238, 15856, 19239, 15858, 19240, 15967, 15865, 19241, 19242, 19243, 19244, 19245, 19246, 19247, 19248, 19249, 19250, 19251, 19252, 19253, 19254, 19255, 15867, 19256, 19257, 19258, 19259, 19260, 19261, 19262, 19263, 19264, 19265, 19266, 15869, 17905, 19267, 19268, 19269, 19270, 19271, 17757, 19272, 17996, 15871, 19273, 19274, 19275, 19276, 15874, 15876, 15879, 15881, 19277, 15883, 17856, 19278, 18030, 15890, 19279, 17893, 19280, 19281, 19282, 19283, 19284, 19285, 18013, 19286, 19287, 19288, 19289, 19290, 19291, 18043, 19292, 19293, 19294, 19295, 19296, 19297, 20543, 20569, 20615, 20554, 20616, 20628, 20544, 20913, 20954, 20986, 21113, 21043, 21053, 21071, 21085, 21087, 21089, 21091, 21293, 15896, 15395, 15397, 15402, 15404, 15406, 15411, 15414, 15416, 15418, 15421, 15423, 15425, 15427, 15430, 15432, 20040, 15434, 15436, 15438, 15440, 15443, 15445, 15447, 15449, 15451, 15453, 15456, 15459, 15461, 15463, 15465, 15467, 15470, 15472, 15474, 15476, 15478, 15480, 15482, 15484, 15486, 15488, 15490, 15492, 15494, 15497, 15499, 15501, 15503, 15507, 20041, 20042, 20043, 20044, 20045, 20046, 20047, 20048, 20049, 20860, 20861, 20862, 20564, 20542, 20574, 20863, 20864, 20865, 20626, 21065, 20545]
tray3 = [21074, 21138, 21167, 21306, 15120, 15123, 18858, 15125, 564, 15131, 15133, 15136, 15138, 15140, 15142, 15144, 15146, 15148, 15150, 15152, 15154, 15157, 15159, 15161, 15163, 15165, 18859, 15168, 18860, 15170, 15172, 15174, 15177, 15179, 15181, 15183, 15185, 15187, 15189, 15192, 15194, 15196, 15198, 15201, 15203, 15205, 15207, 15209, 15211, 18861, 18862, 18863, 18864, 20090, 20873, 15290, 15292, 15295, 15297, 15299, 15301, 15303, 21070, 20876, 21040, 15689, 15691, 15693, 15695, 15697, 15699, 15701, 15703, 15705, 15708, 18875, 18876, 17595, 18877, 20944, 20943, 20945, 21056, 21107, 20961, 20970, 21017, 21025, 21052, 21099, 21101, 21104, 21126, 21155, 21157, 21757, 21127, 21080, 15596, 18899, 15598, 15600, 15602, 18900, 15604, 18901, 15606, 15608, 15611, 15957, 15614, 15616, 15618, 18902, 18903, 21061, 18947, 18948, 15678, 15680, 15682, 15684, 15686, 15710, 15712, 15714, 15717, 15719, 15721, 15723, 15725, 15727, 15729, 15731, 15734, 15736, 15738, 15740, 15742, 15744, 15748, 15750, 15752, 15754, 15756, 17838, 17839, 17837, 17833, 17840, 15668, 15671, 15676, 21308, 574, 570, 16018, 20957, 20959, 17847, 21141, 21143, 15771, 19895, 18070, 19896, 19897, 18080, 19898, 589, 15774, 15776, 19899, 15780, 15784, 15786, 17716, 21064, 19901, 19902, 19903, 19904, 16022, 19905, 19906, 19907, 19908, 19909, 17866, 17871, 19910, 21667, 19912, 18085, 19913, 19914, 15788, 19915, 17952, 19916, 19917, 19918, 19919, 19920, 19921, 19922, 19923, 19924, 19925]
tray4 = [19926, 19927, 19928, 19929, 19930, 19931, 19932, 19933, 18163, 19934, 19935, 19936, 590, 591, 16021, 19937, 15965, 19938, 15790, 19939, 19940, 17828, 17592, 19941, 19942, 19943, 19944, 19945, 19946, 19947, 19948, 19949, 19950, 19951, 15792, 19952, 15796, 15797, 15798, 15800, 15803, 15806, 18141, 15816, 19953, 592, 593, 19954, 15819, 15823, 15826, 15966, 15830, 15832, 15834, 15836, 15837, 15840, 15841, 15844, 15845, 15849, 15851, 15853, 15855, 19955, 15857, 19956, 15859, 19957, 15862, 15866, 19958, 19959, 19960, 19961, 19962, 19963, 19964, 19965, 19966, 19967, 19968, 19969, 19970, 19971, 19972, 15868, 19973, 19974, 19975, 19976, 19977, 19978, 19979, 19980, 19981, 19982, 19983, 15870, 17845, 19984, 19985, 19986, 19987, 19988, 17758, 19989, 16065, 15872, 19990, 19991, 19992, 19993, 594, 15877, 15880, 19994, 15882, 15884, 15887, 19995, 19996, 19997, 15891, 15893, 19998, 19999, 20000, 20002, 20003, 20004, 20005, 20006, 20007, 20008, 20009, 20010, 20011, 20012, 20013, 20014, 20015, 20016, 20017, 20881, 20987, 20955, 21044, 21054, 21072, 21086, 21088, 21090, 21092, 21294, 20145, 20142, 20146, 20144, 15897, 15396, 15398, 15403, 15405, 15407, 15412, 15415, 15417, 15419, 15422, 15424, 15426, 15428, 15431, 15433, 15435, 15437, 15439, 15441, 15444, 15446, 15448, 15450, 15452, 15454, 15457, 15460, 15462, 15464, 15466, 15468, 15471, 15473, 15475, 15477, 15479, 15481, 15483, 15485, 15487, 15489, 15491, 15493, 15495, 15498, 15500, 15502, 15504, 15508, 20060, 20061, 20062, 20063, 20064, 20065, 20066, 20067, 20068, 20069, 20668, 21066, 21297, 21076, 21084, 18505, 18506, 20177, 21082, 21096, 21123, 20001, 17985, 16017]
battery1 = [14787, 14794, 20595, 20530, 20551, 20526, 20836, 20584, 21077, 20938, 20940, 20935, 21128, 20566, 20577, 20591, 20598, 20621, 20998, 21041, 14795, 14804, 14805, 14809, 20537, 20973, 20567, 20568, 15619, 15621, 15623, 15625, 15963, 15964, 15628, 15631, 15633, 15763, 15764, 15765, 15766, 14812, 18198, 14815, 14820, 14823, 14824, 14828, 14833, 14834, 18243, 18244, 14839, 18245, 14841, 14844, 14848, 14851, 14852, 18246, 14853, 14859, 14862, 14863, 14866, 14869, 14871, 14875, 14877, 14879, 14882, 14884, 14886, 14888, 14891, 14895, 14896, 14897, 14899, 14901, 14904, 14905, 14908, 14909, 14911, 14913, 14916, 14918, 14920, 14922, 14924, 14926, 14928, 14931, 14933, 14937, 14939, 14941, 14943, 14945, 14947, 14949, 14952, 14954, 14956, 14959, 14961, 14963, 14966, 14969, 14971, 14973, 14978, 14981, 14983, 14985, 14987, 14990, 14993, 14995, 14997, 14999, 15001, 15003, 15006, 15008, 15010, 15012, 15015, 15017, 15019, 15021, 15026, 15028, 15030, 15032, 15034, 15036, 15041, 15043, 15045, 15047, 15049, 15051, 15053, 15055, 15057, 15060, 15064, 15068, 15071, 15073, 15075, 15077, 15079, 15081, 15083, 15085, 15087, 15090, 15092, 15094, 15097, 15100, 15103, 15105, 15108, 15110, 15112, 15115, 15117, 18002, 18247, 18248, 18249, 18250, 18251, 18063, 18252, 18253, 18254, 18255, 18186, 20837, 20531, 20539, 20562, 20549, 20838, 20594, 20839, 20840, 20540, 20841, 20605, 20624, 20604, 20632, 20634, 17558, 20996, 21012, 21022, 21029, 21075, 21083, 21162, 21160, 15635, 15637, 15639, 15641, 15643, 15645, 18365, 15647, 15650, 15652, 18366, 15654, 15656, 15658, 15659, 15661, 15663, 18367, 18368, 18369, 17928, 17922, 17927, 18370, 21009, 20123, 20536, 20558, 20607, 20932, 21114, 21116, 21301, 21303, 20915, 18495, 15509, 15511, 15978, 15513, 15517, 15519, 15521, 15523, 15525, 15527, 18532, 15530, 15532, 15534, 15536, 15538, 15540, 18533, 20636, 17982, 18498, 18029, 18152, 18151, 20842, 20843, 20844, 20579, 20845, 20846, 20589, 20586, 20981, 20963, 20983, 21001, 15213, 15215, 15217, 17860, 18150, 15221, 15223, 15225, 15232, 15234, 15237, 15239, 17910, 15244, 15246, 15248, 15250, 15252, 15254, 15256, 15258, 15260, 15263, 15265, 15268, 15270, 15272, 18562, 15274, 15276, 18017, 17763, 18019, 18016, 17851, 18563, 18052, 18068, 18051, 18564, 17823, 18059, 20095, 20847, 20848, 20556, 20557, 20891, 20975, 21120, 15541, 15543, 15545, 15547, 15550, 15552, 15554, 15558, 15560, 15564, 15567, 15569, 15573, 15575, 15577, 18571, 15579, 15581, 15582, 15584, 15585, 15587, 15589, 15591, 15593, 15898, 15901, 15903, 18009, 18572, 20534, 20573, 20866, 20528, 20581, 20583, 20631, 20849, 20971, 21093, 21133, 20619, 21037, 15278, 15280, 15282, 15284, 18594, 15287]
battery3 = [19262, 19263, 19264, 19265, 19266, 15869, 17905, 19267, 19268, 19269, 19270, 19271, 17757, 19272, 17996, 15871, 19273, 19274, 19275, 19276, 15874, 15876, 15879, 15881, 19277, 15883, 17856, 19278, 18030, 15890, 19279, 17893, 19280, 19281, 19282, 19283, 19284, 19285, 18013, 19286, 19287, 19288, 19289, 19290, 19291, 18043, 19292, 19293, 19294, 19295, 19296, 19297, 20543, 20569, 20615, 20554, 20616, 20628, 20544, 20913, 20954, 20986, 21113, 21043, 21053, 21071, 21085, 21087, 21089, 21091, 21293, 15896, 15395, 15397, 15402, 15404, 15406, 15411, 15414, 15416, 15418, 15421, 15423, 15425, 15427, 15430, 15432, 20040, 15434, 15436, 15438, 15440, 15443, 15445, 15447, 15449, 15451, 15453, 15456, 15459, 15461, 15463, 15465, 15467, 15470, 15472, 15474, 15476, 15478, 15480, 15482, 15484, 15486, 15488, 15490, 15492, 15494, 15497, 15499, 15501, 15503, 15507, 20041, 20042, 20043, 20044, 20045, 20046, 20047, 20048, 20049, 20860, 20861, 20862, 20564, 20542, 20574, 20863, 20864, 20865, 20626, 21065, 20545]
battery4 = [15733, 15735, 15737, 15739, 15741, 15743, 15747, 15749, 15751, 15753, 15755, 17899, 17900, 17897, 17902, 17903, 20538, 15667, 15670, 15675, 21307, 20956, 20933, 20924, 20925, 20958, 21140, 21142, 15770, 18049, 18038, 19185, 19186, 18149, 19187, 15772, 15773, 15775, 15782, 19189, 15783, 15785, 17857, 21063, 19191, 19192, 19193, 17911, 17932, 19194, 17979, 19195, 19196, 19197, 17919, 17945, 18035, 21666, 19199, 18036, 19200, 19201, 15807, 19202, 18065, 19203, 19204, 19205, 19206, 19207, 19208, 19209, 19210, 18012, 19211, 19212, 19213, 19214, 19215, 19216, 19217, 19218, 19219, 18162, 17864, 19220, 19221, 15808, 15809, 17965, 21031, 19222, 15789, 19223, 15810, 19224, 17865, 17891, 17880, 19225, 17962, 19226, 19227, 19228, 19229, 19230, 19231, 19232, 19233, 19234, 15791, 15811, 15795, 15812, 15802, 15813, 15801, 18157, 15814, 15815, 19236, 15817, 15818, 17855, 19237, 15824, 15827, 15828, 15829, 15831, 15833, 15835, 15838, 15839, 15842, 15843, 15847, 15848, 15850, 15852, 15854, 19238, 15856, 19239, 15858, 19240, 15967, 15865, 19241, 19242, 19243, 19244, 19245, 19246, 19247, 19248, 19249, 19250, 19251, 19252, 19253, 19254, 19255, 15867, 19256, 19257, 19258, 19259, 19260, 19261]
battery2 = [15137, 15139, 15141, 15143, 15145, 15147, 15149, 15151, 15153, 15156, 15158, 15160, 15162, 15164, 18853, 15167, 18854, 15169, 15171, 15173, 15176, 15178, 15180, 15182, 15184, 15186, 15188, 15191, 15193, 15195, 15197, 15200, 15202, 15204, 15206, 15208, 15210, 18855, 18031, 18856, 18857, 20091, 20550, 20563, 20877, 15289, 15291, 15294, 15296, 15298, 15300, 15302, 21069, 20611, 21039, 20612, 20613, 21122, 15688, 15690, 15692, 15694, 15696, 15698, 15700, 15702, 15704, 15707, 18001, 18887, 17896, 18888, 20524, 20525, 20561, 20618, 20946, 20948, 21055, 21106, 20960, 20969, 21016, 21024, 21051, 21098, 21100, 21103, 21125, 21154, 21156, 21756, 17733, 20627, 21079, 15595, 18922, 15597, 15599, 15601, 18923, 15603, 18924, 15605, 15607, 18925, 15613, 15960, 15615, 15617, 18926, 18927, 20560, 21060, 20527, 18945, 18946, 15677, 15679, 15681, 15683, 15685, 15709, 15711, 15713, 15716, 15718, 15720, 15722, 15724, 15726, 15728, 15730]
battery5 = [18595, 17929, 18596, 18597, 20078, 20850, 20851, 20852, 20572, 20548, 20853, 20533, 21130, 21135, 18770, 18771, 15305, 15308, 15311, 18772, 18773, 18774, 18775, 15313, 15316, 15318, 15320, 15322, 15324, 15326, 15328, 18099, 18061, 18776, 18777, 18778, 15332, 15335, 18779, 15337, 18155, 18780, 15339, 15341, 18781, 18782, 15343, 18783, 15345, 18171, 15349, 15351, 15353, 18784, 15355, 18785, 15357, 15359, 15361, 15363, 15365, 15367, 15369, 18786, 15371, 15373, 18787, 15376, 18788, 15378, 15380, 18789, 15382, 15384, 15386, 18790, 15388, 15390, 15393, 15905, 15907, 15909, 15911, 15913, 15915, 15917, 15919, 18791, 17959, 18792, 18793, 18172, 18794, 18795, 18796, 20854, 20855, 20856, 20857, 20858, 20859, 20580, 20582, 21118, 20917, 20535, 20559, 20596, 20622, 20592, 20620, 20555, 20599, 20603, 20641, 20643, 20644, 20645, 20646, 20968, 20936, 17453, 20908, 20907, 20980, 17449, 17532, 21018, 21020, 21005, 21007, 21014, 21026, 21027, 21035, 21058, 21073, 21081, 21095, 21137, 21166, 21305, 15119, 15122, 18852, 15124, 15126, 15130, 15132, 15135]
battery6 = [20634, 17558, 20996, 21012, 21022, 21029, 21075, 21083, 21162, 21160, 15635, 15637, 15639, 15641, 15643, 15645, 18365, 15647, 15650, 15652, 18366, 15654, 15656, 15658, 15659, 15661, 15663, 18367, 18368, 18369, 17928, 17922, 17927, 18370, 21009, 20123, 20536, 20558, 20607, 20932, 21114, 21116, 21301, 21303, 20915, 18495, 15509, 15511, 15978, 15513, 15517, 15519, 15521, 15523, 15525, 15527, 18532, 15530, 15532, 15534, 15536, 15538, 15540, 18533, 20636, 17982, 18498, 18029, 18152, 18151, 20842, 20843, 20844, 20579, 20845, 20846, 20589, 20586, 20981, 20963]
battery7 = [20983, 21001, 15213, 15215, 15217, 17860, 18150, 15221, 15223, 15225, 15232, 15234, 15237, 15239, 17910, 15244, 15246, 15248, 15250, 15252, 15254, 15256, 15258, 15260, 15263, 15265, 15268, 15270, 15272, 18562, 15274, 15276, 18017, 17763, 18019, 18016, 17851, 18563, 18052, 18068, 18051, 18564, 17823, 18059, 20095, 20847, 20848, 20556, 20557, 20891, 20975, 21120, 15541, 15543, 15545, 15547, 15550, 15552, 15554, 15558, 15560, 15564, 15567, 15569, 15573, 15575, 15577, 18571, 15579, 15581, 15582, 15584, 15585, 15587, 15589, 15591, 15593, 15898, 15901, 15903, 18009, 18572, 20534, 20573, 20866, 20528, 20581, 20583, 20631, 20849, 20971, 21093, 21133, 20619, 21037, 15278, 15280, 15282, 15284, 18594, 15287]


class ProductTemplate(models.Model):
    _inherit = "product.template"

    have_design = fields.Boolean('Have Design', default=False)
    attach_design_pdf = fields.Binary('Attach Design (PDF)', compute='_attachment_name', inverse='_set_filename',
                                      copy=False)
    attach_design_pdf_filename = fields.Char('Attach Design (PDF)')
    pdf_attachment_id = fields.Many2one('ir.attachment')
    attach_design_solidworks = fields.Binary('Attach Design (SolidWorks)', compute='_attachment_name_solidwork',
                                             inverse='_set_filename_solidwork', copy=False)
    attach_design_solidworks_filename = fields.Char('Attach Design (SolidWorks)')
    solidword_attach_id = fields.Many2one('ir.attachment')
    calculate_ah = fields.Boolean('Calculate AH Cost', default=False)
    volts = fields.Float('Volts')
    ah = fields.Float('AH')
    product_type = fields.Selection([('battery', 'Battery'), ('cell', 'Cell')], string="Item Type")
    standard_price_temp = fields.Float('Temporary Cost')
    default_code_temp = fields.Char('Temporary Internal Code')
    battery_weight = fields.Float("Battery Weight")

    def update_temp_fields(self):
        prod_template_ids = self.env['product.template'].search([])
        for data in prod_template_ids:
            data.standard_price_temp = data.standard_price
            data.default_code_temp = data.default_code

    @api.onchange('have_design')
    def _onchange_have_design(self):
        if not self.have_design:
            if self.pdf_attachment_id:
                self.pdf_attachment_id.sudo().unlink()
            if self.solidword_attach_id:
                self.solidword_attach_id.sudo().unlink()
            self.attach_design_pdf_filename = ''
            self.attach_design_solidworks_filename = ''
            self.have_design = False

    @api.depends('attach_design_pdf')
    def _attachment_name(self):
        val = self.pdf_attachment_id.datas
        self.attach_design_pdf = val

    def _set_filename(self):
        Attachment = self.env['ir.attachment']
        attachment_value = {
            'name': self.attach_design_pdf_filename or '',
            'datas': self.attach_design_pdf or '',
            'type': 'binary',
            'res_model': "product.template",
            'res_id': self.id,
        }
        attachment = Attachment.sudo().create(attachment_value)
        self.pdf_attachment_id = attachment.id

    @api.depends('attach_design_solidworks')
    def _attachment_name_solidwork(self):
        val = self.solidword_attach_id.datas
        self.attach_design_solidworks = val

    def _set_filename_solidwork(self):
        Attachment = self.env['ir.attachment']
        attachment_value = {
            'name': self.attach_design_solidworks_filename or '',
            'datas': self.attach_design_solidworks or '',
            'type': 'binary',
            'res_model': "product.template",
            'res_id': self.id,
        }
        attachment = Attachment.sudo().create(attachment_value)
        self.solidword_attach_id = attachment.id

    def create_variant(self):
        template_ids = battery7
        counter = 1
        if not template_ids:
            template_ids = [self.id]
        template_brs = self.search([('id', 'in', template_ids)])
        attributes_ms_tray = [
            (0, 0, {
                    'attribute_id': 1,
                    'value_ids': [(6, 0, [1, 2, 3])]
            }), (0, 0, {
                'attribute_id': 2,
                'value_ids': [(6, 0, [4, 5, 6])]
            })
        ]
        attributes_prod = [
            (0, 0, {
                'attribute_id': 1,
                'value_ids': [(6, 0, [1, 2, 3])]
            }), (0, 0, {
                'attribute_id': 2,
                'value_ids': [(6, 0, [4, 5, 6])]
            }),
            (0, 0, {
                'attribute_id': 3,
                'value_ids': [(6, 0, [7, 8, 9, 10, 11, 12])]
            }), (0, 0, {
                'attribute_id': 4,
                'value_ids': [(6, 0, [13, 14, 15])]
            })
        ]
        for temp in template_brs:
            counter += 1
            if not temp.attribute_line_ids:
                if counter % 50 == 0:
                    self._cr.commit()
                temp.write({'attribute_line_ids': attributes_prod})

    @api.model_create_multi
    def create(self, vals_list):
        rec = super(ProductTemplate, self).create(vals_list)
        template_id = self.env.ref('gts_product.product_creation_email_template')
        users_list = self.env['res.users'].search([])
        email_to, email_from = '', ''
        for group_user in users_list:
            if group_user.has_group('gts_product.product_create_email'):
                email_to += group_user.login + ' ,'
        if template_id:
            values = template_id.generate_email(rec.id)
            values['email_to'] = email_to
            values['email_from'] = self.env.user.login
            values['reply_to'] = rec.responsible_id.login
            values['body_html'] = values['body_html']
            mail = self.env['mail.mail'].create(values)
            try:
                mail.send()
            except Exception:
                pass
        return rec


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model_create_multi
    def create(self, vals_list):
        tmpl_obj = self.env['product.template']
        products = super(ProductProduct, self).create(vals_list)
        for data in vals_list:
            print(data)
            if 'product_tmpl_id' in data:
                tmpl_id = tmpl_obj.browse(data['product_tmpl_id'])
                print(tmpl_id.standard_price_temp)
                products.standard_price = tmpl_id.standard_price_temp
                products.default_code = tmpl_id.default_code_temp
        return products

    # custom_standard_price = fields.Float(compute='set_cost',help="")
    #
    # @api.depends('name')
    # def set_cost(self):
    #     products = self.env['product.product'].search([('type','!=','service')])
    #     for product in products:
    #         if product.active:
    #             tot_unit_price=0.0
    #             bills = self.env['account.move.line'].search([('move_id.type', '=', 'in_invoice'), ('product_id', '=', self.id),
    #                  ('move_id.state', '!=', 'cancel')])
    #             po_len = len(bills.purchase_line_id)
    #             for bill in bills:
    #                 # value += bill.quantity * bill.price_unit
    #                 tot_unit_price += bill.price_unit
    #                 # tot_qty += bill.quantity
    #             unit_cost = 0.0
    #             # if value != 0 or tot_qty != 0:
    #             if tot_unit_price != 0 and product.categ_id.property_cost_method == 'average':
    #                 # unit_cost = value / tot_qty
    #                 product.custom_standard_price = tot_unit_price / po_len
    #                 product.standard_price = product.custom_standard_price
    #             else:
    #                 product.custom_standard_price = product.standard_price
    #         else:
    #             product.custom_standard_price = product.standard_price
    #
    #

