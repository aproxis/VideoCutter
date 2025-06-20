import React, { useState } from 'react';
import { 
  Mic, 
  FileAudio, 
  FolderOpen, 
  MessageSquare, 
  Play, 
  Settings, 
  Volume2,
  Sliders,
  Music,
  Headphones,
  Download,
  Upload,
  RefreshCw,
  Save,
  FolderIcon,
  BookOpen,
  Star,
  Trash2
} from 'lucide-react';

const VoiceCloningGUI = () => {
  const [activeMode, setActiveMode] = useState('tts');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showPostProcessing, setShowPostProcessing] = useState(false);
  const [showPresets, setShowPresets] = useState(false);
  const [showInstructions, setShowInstructions] = useState(false);
  const [presetName, setPresetName] = useState('');
  const [savedPresets, setSavedPresets] = useState(() => {
    // Load presets from memory (in a real app, this would be localStorage)
    return {
      'Default TTS': {
        mode: 'tts',
        params: {
          pitch: 0,
          index_rate: 0.3,
          protect: 0.33,
          f0_method: 'rmvpe',
          clean_audio: true,
          export_format: 'WAV'
        }
      },
      'High Quality Speech': {
        mode: 'infer',
        params: {
          pitch: 0,
          index_rate: 0.5,
          protect: 0.5,
          f0_method: 'rmvpe',
          clean_audio: true,
          clean_strength: 0.8,
          upscale_audio: true,
          split_audio: true
        }
      },
      'Singing Voice': {
        mode: 'infer',
        params: {
          pitch: 0,
          index_rate: 0.7,
          protect: 0.2,
          f0_method: 'rmvpe',
          f0_autotune: true,
          post_process: true,
          reverb: true,
          reverb_room_size: 0.3,
          chorus: true
        }
      }
    };
  });
  
  // State for all parameters
  const [params, setParams] = useState({
    // Common parameters
    pitch: 0,
    filter_radius: 3,
    index_rate: 0.3,
    volume_envelope: 1.0,
    protect: 0.33,
    hop_length: 128,
    f0_method: 'rmvpe',
    pth_path: '',
    index_path: '',
    split_audio: false,
    f0_autotune: false,
    clean_audio: false,
    clean_strength: 0.7,
    export_format: 'WAV',
    embedder_model: 'contentvec',
    embedder_model_custom: '',
    upscale_audio: false,
    f0_file: '',
    formant_shifting: false,
    formant_qfrency: 1.0,
    formant_timbre: 1.0,
    sid: 0,
    
    // Infer mode
    input_path: '',
    output_path: '',
    
    // Batch mode
    input_folder: '',
    output_folder: '',
    
    // TTS mode
    tts_text: '',
    tts_voice: '',
    tts_rate: 0,
    output_tts_path: '',
    output_rvc_path: '',
    
    // Post-processing effects
    post_process: false,
    reverb: false,
    pitch_shift: false,
    limiter: false,
    gain: false,
    distortion: false,
    chorus: false,
    bitcrush: false,
    clipping: false,
    compressor: false,
    delay: false,
    
    // Effect parameters
    reverb_room_size: 0.5,
    reverb_damping: 0.5,
    reverb_wet_gain: 0.5,
    reverb_dry_gain: 0.5,
    reverb_width: 0.5,
    reverb_freeze_mode: 0.5,
    pitch_shift_semitones: 0.0,
    limiter_threshold: -6,
    limiter_release_time: 0.01,
    gain_db: 0.0,
    distortion_gain: 25,
    chorus_rate: 1.0,
    chorus_depth: 0.25,
    chorus_center_delay: 7,
    chorus_feedback: 0.0,
    chorus_mix: 0.5,
    bitcrush_bit_depth: 8,
    clipping_threshold: -6,
    compressor_threshold: 0,
    compressor_ratio: 1,
    compressor_attack: 1.0,
    compressor_release: 100,
    delay_seconds: 0.5,
    delay_feedback: 0.0,
    delay_mix: 0.5
  });

  const handleParamChange = (key, value) => {
    setParams(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const generateCommand = () => {
    let command = `python voice_cloning.py ${activeMode}`;
    
    // Add mode-specific required parameters
    if (activeMode === 'infer') {
      command += ` --input_path "${params.input_path}"`;
      command += ` --output_path "${params.output_path}"`;
    } else if (activeMode === 'batch') {
      command += ` --input_folder "${params.input_folder}"`;
      command += ` --output_folder "${params.output_folder}"`;
    } else if (activeMode === 'tts') {
      command += ` --tts_text "${params.tts_text}"`;
      command += ` --tts_voice "${params.tts_voice}"`;
      command += ` --output_tts_path "${params.output_tts_path}"`;
      command += ` --output_rvc_path "${params.output_rvc_path}"`;
      if (params.tts_rate !== 0) command += ` --tts_rate ${params.tts_rate}`;
    }
    
    // Add common required parameters
    command += ` --pth_path "${params.pth_path}"`;
    command += ` --index_path "${params.index_path}"`;
    
    // Add optional parameters (only if different from defaults)
    if (params.pitch !== 0) command += ` --pitch ${params.pitch}`;
    if (params.filter_radius !== 3) command += ` --filter_radius ${params.filter_radius}`;
    if (params.index_rate !== 0.3) command += ` --index_rate ${params.index_rate}`;
    if (params.volume_envelope !== 1.0) command += ` --volume_envelope ${params.volume_envelope}`;
    if (params.protect !== 0.33) command += ` --protect ${params.protect}`;
    if (params.hop_length !== 128) command += ` --hop_length ${params.hop_length}`;
    if (params.f0_method !== 'rmvpe') command += ` --f0_method ${params.f0_method}`;
    if (params.split_audio) command += ` --split_audio`;
    if (params.f0_autotune) command += ` --f0_autotune`;
    if (params.clean_audio) command += ` --clean_audio`;
    if (params.clean_strength !== 0.7) command += ` --clean_strength ${params.clean_strength}`;
    if (params.export_format !== 'WAV') command += ` --export_format ${params.export_format}`;
    if (params.embedder_model !== 'contentvec') command += ` --embedder_model ${params.embedder_model}`;
    if (params.embedder_model_custom) command += ` --embedder_model_custom "${params.embedder_model_custom}"`;
    if (params.upscale_audio) command += ` --upscale_audio`;
    if (params.f0_file) command += ` --f0_file "${params.f0_file}"`;
    if (params.formant_shifting) command += ` --formant_shifting`;
    if (params.formant_qfrency !== 1.0) command += ` --formant_qfrency ${params.formant_qfrency}`;
    if (params.formant_timbre !== 1.0) command += ` --formant_timbre ${params.formant_timbre}`;
    if (params.sid !== 0) command += ` --sid ${params.sid}`;
    
    // Add post-processing effects
    if (params.post_process) command += ` --post_process`;
    if (params.reverb) {
      command += ` --reverb`;
      if (params.reverb_room_size !== 0.5) command += ` --reverb_room_size ${params.reverb_room_size}`;
      if (params.reverb_damping !== 0.5) command += ` --reverb_damping ${params.reverb_damping}`;
      if (params.reverb_wet_gain !== 0.5) command += ` --reverb_wet_gain ${params.reverb_wet_gain}`;
      if (params.reverb_dry_gain !== 0.5) command += ` --reverb_dry_gain ${params.reverb_dry_gain}`;
      if (params.reverb_width !== 0.5) command += ` --reverb_width ${params.reverb_width}`;
      if (params.reverb_freeze_mode !== 0.5) command += ` --reverb_freeze_mode ${params.reverb_freeze_mode}`;
    }
    if (params.pitch_shift) {
      command += ` --pitch_shift`;
      if (params.pitch_shift_semitones !== 0.0) command += ` --pitch_shift_semitones ${params.pitch_shift_semitones}`;
    }
    if (params.limiter) {
      command += ` --limiter`;
      if (params.limiter_threshold !== -6) command += ` --limiter_threshold ${params.limiter_threshold}`;
      if (params.limiter_release_time !== 0.01) command += ` --limiter_release_time ${params.limiter_release_time}`;
    }
    if (params.gain) {
      command += ` --gain`;
      if (params.gain_db !== 0.0) command += ` --gain_db ${params.gain_db}`;
    }
    if (params.distortion) {
      command += ` --distortion`;
      if (params.distortion_gain !== 25) command += ` --distortion_gain ${params.distortion_gain}`;
    }
    if (params.chorus) {
      command += ` --chorus`;
      if (params.chorus_rate !== 1.0) command += ` --chorus_rate ${params.chorus_rate}`;
      if (params.chorus_depth !== 0.25) command += ` --chorus_depth ${params.chorus_depth}`;
      if (params.chorus_center_delay !== 7) command += ` --chorus_center_delay ${params.chorus_center_delay}`;
      if (params.chorus_feedback !== 0.0) command += ` --chorus_feedback ${params.chorus_feedback}`;
      if (params.chorus_mix !== 0.5) command += ` --chorus_mix ${params.chorus_mix}`;
    }
    if (params.bitcrush) {
      command += ` --bitcrush`;
      if (params.bitcrush_bit_depth !== 8) command += ` --bitcrush_bit_depth ${params.bitcrush_bit_depth}`;
    }
    if (params.clipping) {
      command += ` --clipping`;
      if (params.clipping_threshold !== -6) command += ` --clipping_threshold ${params.clipping_threshold}`;
    }
    if (params.compressor) {
      command += ` --compressor`;
      if (params.compressor_threshold !== 0) command += ` --compressor_threshold ${params.compressor_threshold}`;
      if (params.compressor_ratio !== 1) command += ` --compressor_ratio ${params.compressor_ratio}`;
      if (params.compressor_attack !== 1.0) command += ` --compressor_attack ${params.compressor_attack}`;
      if (params.compressor_release !== 100) command += ` --compressor_release ${params.compressor_release}`;
    }
    if (params.delay) {
      command += ` --delay`;
      if (params.delay_seconds !== 0.5) command += ` --delay_seconds ${params.delay_seconds}`;
      if (params.delay_feedback !== 0.0) command += ` --delay_feedback ${params.delay_feedback}`;
      if (params.delay_mix !== 0.5) command += ` --delay_mix ${params.delay_mix}`;
    }
    
    return command;
  };

  const copyCommand = () => {
    navigator.clipboard.writeText(generateCommand());
  };

  const savePreset = () => {
    if (!presetName.trim()) return;
    setSavedPresets(prev => ({
      ...prev,
      [presetName]: {
        mode: activeMode,
        params: { ...params }
      }
    }));
    setPresetName('');
  };

  const loadPreset = (preset) => {
    setActiveMode(preset.mode);
    setParams({ ...params, ...preset.params });
  };

  const deletePreset = (presetKey) => {
    setSavedPresets(prev => {
      const newPresets = { ...prev };
      delete newPresets[presetKey];
      return newPresets;
    });
  };

  const resetSettings = () => {
    setParams({
      // Reset to default values
      pitch: 0,
      filter_radius: 3,
      index_rate: 0.3,
      volume_envelope: 1.0,
      protect: 0.33,
      hop_length: 128,
      f0_method: 'rmvpe',
      pth_path: '',
      index_path: '',
      split_audio: false,
      f0_autotune: false,
      clean_audio: false,
      clean_strength: 0.7,
      export_format: 'WAV',
      embedder_model: 'contentvec',
      embedder_model_custom: '',
      upscale_audio: false,
      f0_file: '',
      formant_shifting: false,
      formant_qfrency: 1.0,
      formant_timbre: 1.0,
      sid: 0,
      input_path: '',
      output_path: '',
      input_folder: '',
      output_folder: '',
      tts_text: '',
      tts_voice: '',
      tts_rate: 0,
      output_tts_path: '',
      output_rvc_path: '',
      post_process: false,
      reverb: false,
      pitch_shift: false,
      limiter: false,
      gain: false,
      distortion: false,
      chorus: false,
      bitcrush: false,
      clipping: false,
      compressor: false,
      delay: false,
      reverb_room_size: 0.5,
      reverb_damping: 0.5,
      reverb_wet_gain: 0.5,
      reverb_dry_gain: 0.5,
      reverb_width: 0.5,
      reverb_freeze_mode: 0.5,
      pitch_shift_semitones: 0.0,
      limiter_threshold: -6,
      limiter_release_time: 0.01,
      gain_db: 0.0,
      distortion_gain: 25,
      chorus_rate: 1.0,
      chorus_depth: 0.25,
      chorus_center_delay: 7,
      chorus_feedback: 0.0,
      chorus_mix: 0.5,
      bitcrush_bit_depth: 8,
      clipping_threshold: -6,
      compressor_threshold: 0,
      compressor_ratio: 1,
      compressor_attack: 1.0,
      compressor_release: 100,
      delay_seconds: 0.5,
      delay_feedback: 0.0,
      delay_mix: 0.5
    });
  };

  const selectFile = async (paramKey) => {
    // In a real application, this would open a file dialog
    // For demo purposes, we'll show how it would work
    try {
      const fileInput = document.createElement('input');
      fileInput.type = 'file';
      fileInput.accept = paramKey.includes('pth') ? '.pth' : 
                        paramKey.includes('index') ? '.index' : 
                        '*';
      fileInput.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
          handleParamChange(paramKey, file.name);
        }
      };
      fileInput.click();
    } catch (error) {
      console.log('File selection not supported in this environment');
    }
  };

  const InputField = ({ label, value, onChange, type = "text", placeholder = "", min, max, step, showFileButton = false, fileKey = "" }) => (
    <div className="space-y-1">
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      <div className="flex space-x-2">
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(type === 'number' ? parseFloat(e.target.value) || 0 : e.target.value)}
          placeholder={placeholder}
          min={min}
          max={max}
          step={step}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
        {showFileButton && (
          <button
            onClick={() => selectFile(fileKey)}
            className="px-3 py-2 bg-gray-100 hover:bg-gray-200 border border-gray-300 rounded-md transition-colors"
            title="Browse for file"
          >
            <FolderIcon className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );

  const SelectField = ({ label, value, onChange, options }) => (
    <div className="space-y-1">
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        {options.map(option => (
          <option key={option.value} value={option.value}>{option.label}</option>
        ))}
      </select>
    </div>
  );

  const CheckboxField = ({ label, checked, onChange, description }) => (
    <div className="flex items-start space-x-3">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
      />
      <div>
        <label className="text-sm font-medium text-gray-700">{label}</label>
        {description && <p className="text-xs text-gray-500 mt-1">{description}</p>}
      </div>
    </div>
  );

  const SliderField = ({ label, value, onChange, min, max, step, description }) => (
    <div className="space-y-2">
      <div className="flex justify-between">
        <label className="text-sm font-medium text-gray-700">{label}</label>
        <span className="text-sm text-gray-500">{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
      />
      {description && <p className="text-xs text-gray-500">{description}</p>}
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Headphones className="h-8 w-8" />
                <div>
                  <h1 className="text-2xl font-bold">Voice Cloning Studio</h1>
                  <p className="text-purple-100">RVC & TTS Interface</p>
                </div>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setShowInstructions(!showInstructions)}
                  className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors flex items-center space-x-2"
                >
                  <BookOpen className="h-4 w-4" />
                  <span>Instructions</span>
                </button>
                <button
                  onClick={() => setShowPresets(!showPresets)}
                  className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors flex items-center space-x-2"
                >
                  <Star className="h-4 w-4" />
                  <span>Presets</span>
                </button>
              </div>
            </div>
          </div>

          {/* Instructions Panel */}
          {showInstructions && (
            <div className="bg-blue-50 border-l-4 border-blue-400 p-6">
              <h3 className="font-bold text-blue-800 mb-4 flex items-center">
                <BookOpen className="h-5 w-5 mr-2" />
                How to Run Locally
              </h3>
              <div className="space-y-4 text-sm text-blue-700">
                <div>
                  <h4 className="font-semibold">1. Prerequisites:</h4>
                  <ul className="list-disc list-inside ml-4 space-y-1">
                    <li>Python 3.8+ installed</li>
                    <li>RVC (Retrieval-based Voice Conversion) library</li>
                    <li>Required Python packages: torch, torchaudio, librosa, soundfile</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold">2. Installation:</h4>
                  <div className="bg-gray-800 text-green-400 p-3 rounded font-mono text-xs">
                    pip install torch torchaudio librosa soundfile numpy scipy<br/>
                    # Install RVC from official repository<br/>
                    git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI<br/>
                    cd Retrieval-based-Voice-Conversion-WebUI<br/>
                    pip install -r requirements.txt
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold">3. Required Files:</h4>
                  <ul className="list-disc list-inside ml-4 space-y-1">
                    <li><strong>.pth file</strong>: Trained RVC model (voice you want to clone to)</li>
                    <li><strong>.index file</strong>: Index file corresponding to the model</li>
                    <li><strong>Input audio</strong>: Source audio file to convert</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold">4. Usage:</h4>
                  <ul className="list-disc list-inside ml-4 space-y-1">
                    <li>Fill in all required fields in the GUI</li>
                    <li>Use the file browser buttons to select model files</li>
                    <li>Copy the generated command from the bottom</li>
                    <li>Run the command in your terminal/command prompt</li>
                  </ul>
                </div>
                <div className="bg-yellow-100 border border-yellow-300 rounded p-3">
                  <p><strong>Note:</strong> This GUI generates the command - you'll need to implement the actual Python script that accepts these arguments and calls the RVC functions.</p>
                </div>
              </div>
            </div>
          )}

          {/* Presets Panel */}
          {showPresets && (
            <div className="bg-green-50 border-l-4 border-green-400 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-green-800 flex items-center">
                  <Star className="h-5 w-5 mr-2" />
                  Saved Presets
                </h3>
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={presetName}
                    onChange={(e) => setPresetName(e.target.value)}
                    placeholder="Preset name..."
                    className="px-3 py-1 border border-gray-300 rounded text-sm"
                  />
                  <button
                    onClick={savePreset}
                    disabled={!presetName.trim()}
                    className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1"
                  >
                    <Save className="h-3 w-3" />
                    <span>Save</span>
                  </button>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {Object.entries(savedPresets).map(([name, preset]) => (
                  <div key={name} className="bg-white rounded-lg p-3 border border-green-200">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-800 truncate">{name}</h4>
                      <button
                        onClick={() => deletePreset(name)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                    <p className="text-xs text-gray-600 mb-2">Mode: {preset.mode.toUpperCase()}</p>
                    <button
                      onClick={() => loadPreset(preset)}
                      className="w-full px-2 py-1 bg-green-100 hover:bg-green-200 text-green-800 rounded text-sm transition-colors"
                    >
                      Load Preset
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Mode Selection */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
              {[
                { id: 'tts', label: 'Text-to-Speech', icon: MessageSquare },
                { id: 'infer', label: 'Single File', icon: FileAudio },
                { id: 'batch', label: 'Batch Process', icon: FolderOpen }
              ].map(mode => (
                <button
                  key={mode.id}
                  onClick={() => setActiveMode(mode.id)}
                  className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-md font-medium transition-colors ${
                    activeMode === mode.id
                      ? 'bg-white text-purple-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  <mode.icon className="h-4 w-4" />
                  <span>{mode.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
            {/* Left Column - Main Settings */}
            <div className="space-y-6">
              {/* Mode-specific inputs */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-800 mb-4 flex items-center">
                  {activeMode === 'tts' && <MessageSquare className="h-5 w-5 mr-2" />}
                  {activeMode === 'infer' && <FileAudio className="h-5 w-5 mr-2" />}
                  {activeMode === 'batch' && <FolderOpen className="h-5 w-5 mr-2" />}
                  {activeMode === 'tts' && 'Text-to-Speech Settings'}
                  {activeMode === 'infer' && 'Single File Settings'}
                  {activeMode === 'batch' && 'Batch Process Settings'}
                </h3>

                {activeMode === 'tts' && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Text to Synthesize</label>
                      <textarea
                        value={params.tts_text}
                        onChange={(e) => handleParamChange('tts_text', e.target.value)}
                        placeholder="Enter the text you want to convert to speech..."
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                    <InputField
                      label="TTS Voice"
                      value={params.tts_voice}
                      onChange={(value) => handleParamChange('tts_voice', value)}
                      placeholder="e.g., en-US-JennyNeural"
                    />
                    <SliderField
                      label="Speaking Rate"
                      value={params.tts_rate}
                      onChange={(value) => handleParamChange('tts_rate', value)}
                      min={-100}
                      max={100}
                      step={1}
                      description="Negative values slow down, positive speed up"
                    />
                    <InputField
                      label="Output TTS Path"
                      value={params.output_tts_path}
                      onChange={(value) => handleParamChange('output_tts_path', value)}
                      placeholder="path/to/output_tts.wav"
                      showFileButton={true}
                      fileKey="output_tts_path"
                    />
                    <InputField
                      label="Output RVC Path"
                      value={params.output_rvc_path}
                      onChange={(value) => handleParamChange('output_rvc_path', value)}
                      placeholder="path/to/output_rvc.wav"
                      showFileButton={true}
                      fileKey="output_rvc_path"
                    />
                  </div>
                )}

                {activeMode === 'infer' && (
                  <div className="space-y-4">
                    <InputField
                      label="Input Audio Path"
                      value={params.input_path}
                      onChange={(value) => handleParamChange('input_path', value)}
                      placeholder="path/to/input.wav"
                      showFileButton={true}
                      fileKey="input_path"
                    />
                    <InputField
                      label="Output Audio Path"
                      value={params.output_path}
                      onChange={(value) => handleParamChange('output_path', value)}
                      placeholder="path/to/output.wav"
                      showFileButton={true}
                      fileKey="output_path"
                    />
                  </div>
                )}

                {activeMode === 'batch' && (
                  <div className="space-y-4">
                    <InputField
                      label="Input Folder"
                      value={params.input_folder}
                      onChange={(value) => handleParamChange('input_folder', value)}
                      placeholder="path/to/input/folder"
                      showFileButton={true}
                      fileKey="input_folder"
                    />
                    <InputField
                      label="Output Folder"
                      value={params.output_folder}
                      onChange={(value) => handleParamChange('output_folder', value)}
                      placeholder="path/to/output/folder"
                      showFileButton={true}
                      fileKey="output_folder"
                    />
                  </div>
                )}
              </div>

              {/* Required Model Files */}
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <h3 className="font-semibold text-red-800 mb-4 flex items-center">
                  <Upload className="h-5 w-5 mr-2" />
                  Required Model Files
                </h3>
                <div className="space-y-4">
                  <InputField
                    label="RVC Model Path (.pth)"
                    value={params.pth_path}
                    onChange={(value) => handleParamChange('pth_path', value)}
                    placeholder="path/to/model.pth"
                    showFileButton={true}
                    fileKey="pth_path"
                  />
                  <InputField
                    label="Index File Path (.index)"
                    value={params.index_path}
                    onChange={(value) => handleParamChange('index_path', value)}
                    placeholder="path/to/model.index"
                    showFileButton={true}
                    fileKey="index_path"
                  />
                </div>
              </div>

              {/* Basic Voice Settings */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-800 mb-4 flex items-center">
                  <Volume2 className="h-5 w-5 mr-2" />
                  Voice Settings
                </h3>
                <div className="space-y-4">
                  <SliderField
                    label="Pitch"
                    value={params.pitch}
                    onChange={(value) => handleParamChange('pitch', value)}
                    min={-24}
                    max={24}
                    step={1}
                    description="Adjust the pitch of the output voice"
                  />
                  <SliderField
                    label="Index Rate"
                    value={params.index_rate}
                    onChange={(value) => handleParamChange('index_rate', value)}
                    min={0}
                    max={1}
                    step={0.01}
                    description="Higher values mean stronger model influence"
                  />
                  <SliderField
                    label="Protect"
                    value={params.protect}
                    onChange={(value) => handleParamChange('protect', value)}
                    min={0}
                    max={1}
                    step={0.01}
                    description="Protect consonants and breathing sounds"
                  />
                  <SelectField
                    label="F0 Method"
                    value={params.f0_method}
                    onChange={(value) => handleParamChange('f0_method', value)}
                    options={[
                      { value: 'rmvpe', label: 'RMVPE (Recommended)' },
                      { value: 'crepe', label: 'Crepe' },
                      { value: 'harvest', label: 'Harvest' },
                      { value: 'dio', label: 'DIO' },
                      { value: 'pm', label: 'PM' }
                    ]}
                  />
                </div>
              </div>

              {/* Quick Options */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="font-semibold text-green-800 mb-4">Quick Options</h3>
                <div className="space-y-3">
                  <CheckboxField
                    label="Clean Audio"
                    checked={params.clean_audio}
                    onChange={(value) => handleParamChange('clean_audio', value)}
                    description="Recommended for speech conversions"
                  />
                  <CheckboxField
                    label="F0 Autotune"
                    checked={params.f0_autotune}
                    onChange={(value) => handleParamChange('f0_autotune', value)}
                    description="Useful for singing voice conversions"
                  />
                  <CheckboxField
                    label="Split Audio"
                    checked={params.split_audio}
                    onChange={(value) => handleParamChange('split_audio', value)}
                    description="Better quality for longer audio files"
                  />
                  <CheckboxField
                    label="Upscale Audio"
                    checked={params.upscale_audio}
                    onChange={(value) => handleParamChange('upscale_audio', value)}
                    description="Improve quality of low-quality input"
                  />
                </div>
              </div>
            </div>

            {/* Right Column - Advanced Settings */}
            <div className="space-y-6">
              {/* Advanced Settings Toggle */}
              <button
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="w-full flex items-center justify-between p-4 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <Settings className="h-5 w-5" />
                  <span className="font-medium">Advanced Settings</span>
                </div>
                <div className={`transform transition-transform ${showAdvanced ? 'rotate-180' : ''}`}>
                  ▼
                </div>
              </button>

              {showAdvanced && (
                <div className="space-y-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-800 mb-3">Audio Processing</h4>
                    <div className="space-y-3">
                      <SliderField
                        label="Filter Radius"
                        value={params.filter_radius}
                        onChange={(value) => handleParamChange('filter_radius', value)}
                        min={0}
                        max={10}
                        step={1}
                      />
                      <SliderField
                        label="Volume Envelope"
                        value={params.volume_envelope}
                        onChange={(value) => handleParamChange('volume_envelope', value)}
                        min={0}
                        max={1}
                        step={0.01}
                      />
                      <SliderField
                        label="Clean Strength"
                        value={params.clean_strength}
                        onChange={(value) => handleParamChange('clean_strength', value)}
                        min={0}
                        max={1}
                        step={0.01}
                      />
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-800 mb-3">Model Settings</h4>
                    <div className="space-y-3">
                      <SelectField
                        label="Embedder Model"
                        value={params.embedder_model}
                        onChange={(value) => handleParamChange('embedder_model', value)}
                        options={[
                          { value: 'contentvec', label: 'ContentVec' },
                          { value: 'hubert', label: 'HuBERT' },
                          { value: 'custom', label: 'Custom' }
                        ]}
                      />
                      {params.embedder_model === 'custom' && (
                        <InputField
                          label="Custom Embedder Path"
                          value={params.embedder_model_custom}
                          onChange={(value) => handleParamChange('embedder_model_custom', value)}
                        />
                      )}
                      <InputField
                        label="Speaker ID"
                        type="number"
                        value={params.sid}
                        onChange={(value) => handleParamChange('sid', value)}
                        min={0}
                      />
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-800 mb-3">Formant Shifting</h4>
                    <div className="space-y-3">
                      <CheckboxField
                        label="Enable Formant Shifting"
                        checked={params.formant_shifting}
                        onChange={(value) => handleParamChange('formant_shifting', value)}
                      />
                      {params.formant_shifting && (
                        <>
                          <SliderField
                            label="Formant Frequency"
                            value={params.formant_qfrency}
                            onChange={(value) => handleParamChange('formant_qfrency', value)}
                            min={0.5}
                            max={2}
                            step={0.01}
                          />
                          <SliderField
                            label="Formant Timbre"
                            value={params.formant_timbre}
                            onChange={(value) => handleParamChange('formant_timbre', value)}
                            min={0.5}
                            max={2}
                            step={0.01}
                          />
                        </>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Post-Processing Effects */}
              <button
                onClick={() => setShowPostProcessing(!showPostProcessing)}
                className="w-full flex items-center justify-between p-4 bg-purple-100 hover:bg-purple-200 rounded-lg transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <Music className="h-5 w-5" />
                  <span className="font-medium">Post-Processing Effects</span>
                </div>
                <div className={`transform transition-transform ${showPostProcessing ? 'rotate-180' : ''}`}>
                  ▼
                </div>
              </button>

              {showPostProcessing && (
                <div className="space-y-4">
                  <CheckboxField
                    label="Enable Post-Processing"
                    checked={params.post_process}
                    onChange={(value) => handleParamChange('post_process', value)}
                  />
                  
                  {params.post_process && (
                    <div className="space-y-4">
                      {/* Reverb */}
                      <div className="bg-gray-50 rounded-lg p-4">
                        <CheckboxField
                          label="Reverb"
                          checked={params.reverb}
                          onChange={(value) => handleParamChange('reverb', value)}
                        />
                        {params.reverb && (
                          <div className="mt-3 space-y-2">
                            <SliderField
                              label="Room Size"
                              value={params.reverb_room_size}
                              onChange={(value) => handleParamChange('reverb_room_size', value)}
                              min={0}
                              max={1}
                              step={0.01}
                            />
                            <SliderField
                              label="Damping"
                              value={params.reverb_damping}
                              onChange={(value) => handleParamChange('reverb_damping', value)}
                              min={0}
                              max={1}
                              step={0.01}
                            />
                            <SliderField
                              label="Wet Gain"
                              value={params.reverb_wet_gain}
                              onChange={(value) => handleParamChange('reverb_wet_gain', value)}
                              min={0}
                              max={1}
                              step={0.01}
                            />
                            <SliderField
                              label="Dry Gain"
                              value={params.reverb_dry_gain}
                              onChange={(value) => handleParamChange('reverb_dry_gain', value)}
                              min={0}
                              max={1}
                              step={0.01}
                            />
                          </div>
                        )}
                      </div>

                      {/* Pitch Shift */}
                      <div className="bg-gray-50 rounded-lg p-4">
                        <CheckboxField
                          label="Pitch Shift"
                          checked={params.pitch_shift}
                          onChange={(value) => handleParamChange('pitch_shift', value)}
                        />
                        {params.pitch_shift && (
                          <div className="mt-3">
                            <SliderField
                              label="Semitones"
                              value={params.pitch_shift_semitones}
                              onChange={(value) => handleParamChange('pitch_shift_semitones', value)}
                              min={-12}
                              max={12}
                              step={0.1}
                            />
                          </div>
                        )}
                      </div>

                      {/* Limiter */}
                      <div className="bg-gray-50 rounded-lg p-4">
                        <CheckboxField
                          label="Limiter"
                          checked={params.limiter}
                          onChange={(value) => handleParamChange('limiter', value)}
                        />
                        {params.limiter && (
                          <div className="mt-3 space-y-2">
                            <SliderField
                              label="Threshold (dB)"
                              value={params.limiter_threshold}
                              onChange={(value) => handleParamChange('limiter_threshold', value)}
                              min={-20}
                              max={0}
                              step={0.1}
                            />
                            <SliderField
                              label="Release Time"
                              value={params.limiter_release_time}
                              onChange={(value) => handleParamChange('limiter_release_time', value)}
                              min={0.001}
                              max={1}
                              step={0.001}
                            />
                          </div>
                        )}
                      </div>

                      {/* Gain */}
                      <div className="bg-gray-50 rounded-lg p-4">
                        <CheckboxField
                          label="Gain"
                          checked={params.gain}
                          onChange={(value) => handleParamChange('gain', value)}
                        />
                        {params.gain && (
                          <div className="mt-3">
                            <SliderField
                              label="Gain (dB)"
                              value={params.gain_db}
                              onChange={(value) => handleParamChange('gain_db', value)}
                              min={-20}
                              max={20}
                              step={0.1}
                            />
                          </div>
                        )}
                      </div>

                      {/* Distortion */}
                      <div className="bg-gray-50 rounded-lg p-4">
                        <CheckboxField
                          label="Distortion"
                          checked={params.distortion}
                          onChange={(value) => handleParamChange('distortion', value)}
                        />
                        {params.distortion && (
                          <div className="mt-3">
                            <SliderField
                              label="Gain"
                              value={params.distortion_gain}
                              onChange={(value) => handleParamChange('distortion_gain', value)}
                              min={1}
                              max={100}
                              step={1}
                            />
                          </div>
                        )}
                      </div>

                      {/* Chorus */}
                      <div className="bg-gray-50 rounded-lg p-4">
                        <CheckboxField
                          label="Chorus"
                          checked={params.chorus}
                          onChange={(value) => handleParamChange('chorus', value)}
                        />
                        {params.chorus && (
                          <div className="mt-3 space-y-2">
                            <SliderField
                              label="Rate"
                              value={params.chorus_rate}
                              onChange={(value) => handleParamChange('chorus_rate', value)}
                              min={0.1}
                              max={10}
                              step={0.1}
                            />
                            <SliderField
                              label="Depth"
                              value={params.chorus_depth}
                              onChange={(value) => handleParamChange('chorus_depth', value)}
                              min={0}
                              max={1}
                              step={0.01}
                            />
                            <SliderField
                              label="Mix"
                              value={params.chorus_mix}
                              onChange={(value) => handleParamChange('chorus_mix', value)}
                              min={0}
                              max={1}
                              step={0.01}
                            />
                          </div>
                        )}
                      </div>

                      {/* Other Effects */}
                      <div className="grid grid-cols-2 gap-2">
                        <CheckboxField
                          label="Bitcrush"
                          checked={params.bitcrush}
                          onChange={(value) => handleParamChange('bitcrush', value)}
                        />
                        <CheckboxField
                          label="Clipping"
                          checked={params.clipping}
                          onChange={(value) => handleParamChange('clipping', value)}
                        />
                        <CheckboxField
                          label="Compressor"
                          checked={params.compressor}
                          onChange={(value) => handleParamChange('compressor', value)}
                        />
                        <CheckboxField
                          label="Delay"
                          checked={params.delay}
                          onChange={(value) => handleParamChange('delay', value)}
                        />
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Output Settings */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h3 className="font-semibold text-yellow-800 mb-4 flex items-center">
                  <Download className="h-5 w-5 mr-2" />
                  Output Settings
                </h3>
                <SelectField
                  label="Export Format"
                  value={params.export_format}
                  onChange={(value) => handleParamChange('export_format', value)}
                  options={[
                    { value: 'WAV', label: 'WAV' },
                    { value: 'MP3', label: 'MP3' },
                    { value: 'FLAC', label: 'FLAC' },
                    { value: 'OGG', label: 'OGG' }
                  ]}
                />
              </div>
            </div>
          </div>

          {/* Command Output */}
          <div className="border-t border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-800 flex items-center">
                <RefreshCw className="h-5 w-5 mr-2" />
                Generated Command
              </h3>
              <button
                onClick={copyCommand}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2"
              >
                <Download className="h-4 w-4" />
                <span>Copy Command</span>
              </button>
            </div>
            <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto">
              <pre className="whitespace-pre-wrap break-all">{generateCommand()}</pre>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="bg-gray-50 px-6 py-4 flex justify-between items-center">
            <div className="text-sm text-gray-600">
              {activeMode === 'tts' && 'Text-to-Speech + RVC Processing'}
              {activeMode === 'infer' && 'Single File Voice Conversion'}
              {activeMode === 'batch' && 'Batch Voice Conversion'}
            </div>
            <div className="flex space-x-3">
              <button className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
                Reset
              </button>
              <button className="px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-colors flex items-center space-x-2">
                <Play className="h-4 w-4" />
                <span>Process Audio</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceCloningGUI;