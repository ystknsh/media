Of course, here is the manual based on the provided video.

***

# MulmoCast: Creating Lip-Sync Videos

This manual explains how to generate a video where the character's mouth moves in sync with the audio narration. This process requires a valid **Replicate API Token**.

## 1. Project and Style Setup

Before generating content, set up your project's style and canvas dimensions.

1.  (00:01) (Start a new project by clicking **+ Create New** from the Dashboard.)
2.  (00:03) Navigate to the **Style** tab.
3.  **00:05** In the **Style template** section, select a style that includes a character. In this example, **Presentation by Ani** is chosen.
4.  **00:08** Click **Apply Style**. This will automatically populate settings for voice, image style, and character.
5.  **00:13** Scroll down to the **Canvas Size** section and select a landscape **Size Preset** from the dropdown menu, such as **1792x1024**.

## 2. Configuring the Replicate API Token

Lip-sync functionality is provided by Replicate, so an API token is required.

1.  (00:31) Click the **Settings** icon in the top-right corner.
2.  (00:33) In the Settings menu, click to expand the **API Key Settings** section.
3.  **00:35** Enter your API key into the **Replicate API Token** field.
4.  **00:39** Close the menu to save the settings. A "Settings saved" notification will confirm the change.

> **Important:** Lip-sync generation will fail if the Replicate API Token is not correctly configured.

## 3. Generating the Character Image

First, create the static image that will be animated.

1.  (00:48) Navigate to the **BEAT** tab. The character ("ani") should already be selected under **Character Image**.
2.  **00:59** Enter the narration text into the main script input field. For example: `Now let's talk about lip sync. It means my mouth moves along with my voice...`
3.  **01:08** In the **Image Generation Prompt** field, describe the scene. You only need to describe the character's clothing and the background, not the character's face. For example: `in mountain climbing gear, on a rocky trail with green forest behind, daylight.`
4.  **01:10** Click the magic wand icon to generate the image.
5.  **03:17** The static image will be created and displayed in the preview area.

## 4. Generating the Lip-Sync Video

With the script and image ready, you can now generate the lip-sync animation.

1.  **06:15** Check the **LipSync** checkbox located below the Movie Prompt field.
2.  **06:20** Click the magic wand icon that appears next to the LipSync checkbox. The system will begin generating the audio and the corresponding lip-sync animation.
3.  **08:26** The animated video with lip-sync will appear in the "Video Preview" area.
4.  (08:36) (Click the preview to open a larger player and watch the character speak in sync with the generated audio.)

## 5. Finalizing and Downloading the Video

Finally, render the complete video file.

1.  **08:54** Click the main **Generate Video** button in the "Create Video / Watch Video" panel on the right.
2.  **09:09** The final video will render and appear in the **Movie Preview** player.
3.  (09:18) (Click **Play** to review the final output.)
4.  **09:37** Click the **Download MP4** button to save the video file to your computer.