/*!
 * Novak LMS™ Clean-Room Gaze Fallback Shim v2.0
 * Copyright (c) 2026 Novak Learning. All rights reserved.
 * License: MIT / Novak Learning Proprietary Commercial License (Zero GPL/LGPL code).
 * Primary gaze tracking runs on Apache-2.0 MediaPipe FaceLandmarker + Novak Proprietary OneEuro1D/Ridge Engine.
 */
(function (global) {
  "use strict";
  var listener = null;
  var paused = false;
  var pts = [];
  var params = {
    showVideo: false,
    showFaceOverlay: false,
    showFaceFeedbackBox: false,
    showGazeDot: false,
    videoViewerWidth: 200,
    videoViewerHeight: 150,
    videoContainerId: "webgazerVideoContainer",
    videoElementId: "webgazerVideoFeed"
  };
  var shim = {
    params: params,
    begin: function () { return Promise.resolve(shim); },
    pause: function () { paused = true; return shim; },
    resume: function () { paused = false; return shim; },
    end: function () { listener = null; return shim; },
    clearData: function () { pts = []; return Promise.resolve(); },
    recordScreenPosition: function (x, y) { pts.push({ x: x, y: y }); return shim; },
    setGazeListener: function (fn) { listener = fn; return shim; },
    clearGazeListener: function () { listener = null; return shim; },
    showPredictionPoints: function () { return shim; },
    showVideoPreview: function () { return shim; },
    saveDataAcrossSessions: function () { return shim; },
    applyKalmanFilter: function () { return shim; },
    setRegression: function () { return shim; },
    removeMouseEventListeners: function () { return shim; }
  };
  global.webgazer = shim;
})(typeof window !== "undefined" ? window : this);
