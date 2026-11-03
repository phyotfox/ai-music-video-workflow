/*  To The Moon · After Effects builder
    Run in After Effects: File > Scripts > Run Script File...  (select this file)
    Builds comp "TTM_FINAL": master picture + lyric captions (word-timed) + beat motion with sliders.
    Re-run any time; it makes a fresh comp each run.                                                */
(function () {
    var FONT_MAIN = "Doto-Bold";          // Google font "Doto" (dot matrix). Install it, or change here.
    var FONT_FALLBACK = "Menlo-Bold";      // used automatically if Doto isn't installed
    var MASTER_NAME = "ToTheMoon_cut-v10_master_ProRes422HQ.mov";
    var DUR = 75.4583, FPS = 24;
    var LINES = __LINES__;
    var BEATS = __BEATS__;
    var DOWNS = __DOWNS__;
    var ZONES = [[30.95, 45.28], [63.19, 70.36]];           // drop + build: punches and flashes
    var SHAKE_ZONE = [63.19, 72.42];                         // build + final hit: shake ramps up

    app.beginUndoGroup("To The Moon build");
    var proj = app.project || app.newProject();

    // ---------- master footage ----------
    var here = File($.fileName).parent;
    var mf = new File(here.parent.fsName + "/07_master/" + MASTER_NAME);
    if (!mf.exists) { mf = File.openDialog("Locate " + MASTER_NAME); if (!mf) { alert("Master not found."); return; } }
    var footage = proj.importFile(new ImportOptions(mf));

    var comp = proj.items.addComp("TTM_FINAL", 1920, 1080, 1, DUR, FPS);
    comp.bgColor = [0, 0, 0];
    var master = comp.layers.add(footage);
    master.name = "MASTER (picture + song)";

    // ---------- control null ----------
    var ctl = comp.layers.addNull(DUR);
    ctl.name = "BEAT_CONTROL";
    ctl.label = 9;
    function slider(nm, v) { var s = ctl.Effects.addProperty("ADBE Slider Control"); s.name = nm; s.property(1).setValue(v); }
    function check(nm, v) { var c = ctl.Effects.addProperty("ADBE Checkbox Control"); c.name = nm; c.property(1).setValue(v ? 1 : 0); }
    slider("Punch (scale %)", 4);
    slider("Flash (opacity %)", 35);
    slider("Shake (px)", 18);
    check("Captions On", true);
    // beat markers for reference (downbeats labelled with bar number)
    var mk = ctl.property("Marker");
    for (var d = 0; d < DOWNS.length; d++) mk.setValueAtTime(DOWNS[d], new MarkerValue("BAR " + (d + 1)));
    var cm = comp.markerProperty;
    var SECTIONS = [[0.53,"Intro"],[4.11,"Verse"],[14.85,"Intercom"],[22.0,"Pre-drop"],[30.95,"DROP"],[45.28,"Descent"],[52.44,"Break"],[63.19,"BUILD"],[70.36,"FINAL HIT"],[72.15,"Whisper"]];
    for (var s = 0; s < SECTIONS.length; s++) cm.setValueAtTime(SECTIONS[s][0], new MarkerValue(SECTIONS[s][1]));

    var ARR = "var B=" + BEATS.toSource() + ";var D=" + DOWNS.toSource() + ";var Z=" + ZONES.toSource() + ";";
    var FN = "function last(a,t){var l=-99;for(var i=0;i<a.length;i++){if(a[i]<=t)l=a[i];else break;}return l;}" +
             "function inZ(t){for(var i=0;i<Z.length;i++){if(t>=Z[i][0]&&t<Z[i][1])return true;}return false;}";
    var C = "var C=thisComp.layer(\"BEAT_CONTROL\");";

    // ---------- beat punch + shake on the master layer ----------
    master.transform.scale.expression = ARR + FN + C +
        "var p=C.effect(\"Punch (scale %)\")(1);var sh=C.effect(\"Shake (px)\")(1);var t=time;var k=0;" +
        "if(inZ(t)){k=p*Math.exp(-(t-last(B,t))/0.08)+p*1.6*Math.exp(-(t-last(D,t))/0.10);}" +
        "var r=(t>=" + SHAKE_ZONE[0] + "&&t<" + SHAKE_ZONE[1] + ")?(t-" + SHAKE_ZONE[0] + ")/(" + (SHAKE_ZONE[1]-SHAKE_ZONE[0]) + "):0;" +
        "var m=r>0?(sh*r*2/1920*100+1):0;var s=100+k+m;[s,s];";
    master.transform.position.expression = C +
        "var sh=C.effect(\"Shake (px)\")(1);var t=time;var r=(t>=" + SHAKE_ZONE[0] + "&&t<" + SHAKE_ZONE[1] + ")?(t-" + SHAKE_ZONE[0] + ")/(" + (SHAKE_ZONE[1]-SHAKE_ZONE[0]) + "):0;" +
        "value+(r>0?(wiggle(14,sh*r*r)-value):[0,0]);";

    // ---------- downbeat flash ----------
    var flash = comp.layers.addSolid([1, 1, 1], "FLASH (downbeats)", 1920, 1080, 1, DUR);
    flash.blendingMode = BlendingMode.ADD;
    flash.transform.opacity.expression = ARR + FN + C +
        "var f=C.effect(\"Flash (opacity %)\")(1);var t=time;var o=0;" +
        "if(inZ(t)){o=f*Math.exp(-(t-last(D,t))/0.05);}" +
        "if(t>=70.36&&t<70.6){o=Math.max(o,100*Math.exp(-(t-70.36)/0.08));}o;";
    flash.label = 1;

    // ---------- lyric captions ----------
    function setFont(doc, size) {
        doc.font = (HAS_MAIN ? FONT_MAIN : FONT_FALLBACK);
        doc.fontSize = size; doc.applyFill = true; doc.fillColor = [1, 1, 1];
        doc.applyStroke = false; doc.justification = ParagraphJustification.CENTER_JUSTIFY;
        doc.tracking = 40;
        return doc;
    }
    var HAS_MAIN = true;
    try { if (app.fonts && app.fonts.getFontsByPostScriptName) { var ff = app.fonts.getFontsByPostScriptName(FONT_MAIN); HAS_MAIN = !!(ff && ff.length); } } catch (e) {}
    var STY = { small: { size: 44, y: 950 }, verse: { size: 58, y: 940 }, chant: { size: 190, y: 600 } };
    for (var i = LINES.length - 1; i >= 0; i--) {
        var L = LINES[i], st = STY[L.style];
        var tl = comp.layers.addText(L.w.join(" "));
        tl.name = "LYR " + ("0" + (i + 1)).slice(-2) + " · " + L.w.join(" ");
        tl.label = L.style === "chant" ? 11 : 14;
        var tp = tl.property("Source Text");
        var doc = setFont(tp.value, st.size);
        if (L.style === "chant") doc.text = L.w.join(" ").toUpperCase();
        tp.setValue(doc);
        var wArr = (L.style === "chant" ? L.w.join("|").toUpperCase().split("|") : L.w).toSource();
        var tArr = L.t.toSource();
        if (L.style === "chant") {   // one big word at a time
            tp.expression = "var w=" + wArr + ";var t=" + tArr + ";var s=\"\";for(var i=0;i<t.length;i++){if(time>=t[i])s=w[i];}s;";
            tl.transform.scale.expression = "var t=" + tArr + ";var ws=-99;for(var i=0;i<t.length;i++){if(time>=t[i])ws=t[i];}var k=18*Math.exp(-(time-ws)/0.09);[100+k,100+k];";
        } else {                     // words build up as they are sung
            tp.expression = "var w=" + wArr + ";var t=" + tArr + ";var s=\"\";for(var i=0;i<t.length;i++){if(time>=t[i])s+=(s?\" \":\"\")+w[i];}s;";
        }
        tl.transform.position.setValue([960, st.y]);
        tl.transform.opacity.expression = "thisComp.layer(\"BEAT_CONTROL\").effect(\"Captions On\")(1)*100;";
        var ds = tl.Effects.addProperty("ADBE Drop Shadow");
        ds.property("Opacity").setValue(160); ds.property("Distance").setValue(4); ds.property("Softness").setValue(12);
        tl.inPoint = Math.max(0, L.t[0] - 0.04);
        tl.outPoint = Math.min(DUR, L.end + (L.style === "chant" ? 0.12 : 0.45));
    }

    ctl.moveToBeginning();
    comp.openInViewer();
    app.endUndoGroup();
    alert((HAS_MAIN ? "" : "Font Doto not found, used " + FONT_FALLBACK + ". Install Doto from Google Fonts and change FONT_MAIN if you want the dot-matrix look.\n\n") + "TTM_FINAL built.\n\nControls: layer BEAT_CONTROL > Effect Controls (Punch, Flash, Shake, Captions On).\nCaptions: layers named LYR … (edit font/size/position freely).");
})();
