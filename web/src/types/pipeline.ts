export interface StoryCharacter {
  characterId: string;
  name: string;
  characterPrompt: string;
  imageUrl?: string;
}

export interface StoryScene {
  sceneNumber: number;
  sceneDescription: string;
  audioText: string;
  characterIds: string[];
  characterContext: string;
  settingPrompt: string;
  startingSettingPrompt?: string;
  endingSettingPrompt?: string;
  motionPrompt?: string;
  durationSeconds: number;
  settingImageUrl?: string;
  compositeImageUrl?: string;
  videoUrl?: string;
}

export interface StoryData {
  theme?: string;
  characters: StoryCharacter[];
  scenes: StoryScene[];
}

export type PipelineStage = 'idle' | 'story' | 'assets' | 'compositing' | 'videos' | 'complete';
