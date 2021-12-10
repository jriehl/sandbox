/**
 * Starts with three/examp
 */

import * as THREE from 'three';

import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

let camera, scene, renderer, video;

function init() {
    camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.z = 0.01;

    scene = new THREE.Scene();

    video = document.getElementById('video');

    const texture = new THREE.VideoTexture(video);

    const geometry = new THREE.PlaneGeometry(16, 9);
    geometry.scale(0.5, 0.5, 0.5);
    const material = new THREE.MeshBasicMaterial({map: texture});

    const texture2 = new THREE.TextureLoader().load('dist/play.png');

    const geometry2 = new THREE.PlaneGeometry(6, 9);
    geometry2.scale(0.5, 0.5, 0.5);
    const material2 = new THREE.MeshBasicMaterial({map: texture2});

    const count = 128;
    const radius = 32;

    for (let i=1, l=count; i <= l; i++) {
        const phi = Math.acos(-1 + (2 * i) / l);
        const theta = Math.sqrt(l * Math.PI) * phi;
        const mesh = new THREE.Mesh(
            (i % 2 == 0) ? geometry : geometry2,
            (i % 2 == 0) ? material : material2
        );
        mesh.position.setFromSphericalCoords(radius, phi, theta);
        mesh.lookAt(camera.position);
        scene.add(mesh);
    }

    renderer = new THREE.WebGLRenderer({antialias: true});
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    const viewport = document.getElementById('viewport');
    viewport.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableZoom = false;
    controls.enablePan = false;

    window.addEventListener('resize', onWindowResize);

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const constraints = {video: {width: 1280, height: 720, facingMode: 'user'}};

        navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
            video.srcObject = stream;
            video.play();
        }).catch(function (error) {
            console.error('Unable to access the camera/webcam.', error);
        });
    } else {
        console.error('MediaDevices interface not available.');
    }

    const button = document.getElementById('thebutton');
    button.onclick = function (event) {
        if (!document.fullscreenElement) {
            document.body.requestFullscreen().catch((err) => {
                alert(`Could not enable full-screen: ${err.message} (${err.name})`);
            });
        } else {
            document.exitFullscreen();
        }
    };
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    renderer.setSize(window.innerWidth, window.innerHeight);
}

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

init();
animate();
