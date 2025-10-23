Of course, here is the manual based on the provided video.

***

# MulmoCast: Generating Images and Videos with Google AI

This manual explains how to use the Google provider within MulmoCast to generate images and create videos from those images.

## 1. Initial Setup: Selecting the Google Provider

Before generating content, you must select Google as the video generation provider in the project settings.

1.  **00:10** Start a new project by clicking the **+ Create New** button from the Dashboard.
2.  **00:12** Navigate to the **Style** tab in the "Create Video Story" editor.
3.  **00:14** Scroll down to the **Movie Parameters** section.
4.  **00:16** Click the **Provider** dropdown menu and select **Google**. This ensures that the video generation will be processed by Google's AI model.

> **Note:** Proper API keys must be configured in the main **Settings** menu (accessible from the Dashboard) for generation to work. This was briefly shown from **00:01** to **00:09**.

## 2. How to Generate an Image

First, create a static image that will serve as the base for your video.

1.  **00:19** Return to the **BEAT** tab.
2.  **00:24** Enter the presenter's voice content or a scene description in the text field (e.g., "introduction").
3.  **00:29** In the **Image Generation Prompt** field, type a detailed description of the image you want to create. For example: `Blue whale swimming under sunlight in deep ocean, facing left, cinematic lighting.`
4.  **00:31** Click the magic wand icon next to the prompt field to start the generation. You will see a "Generating..." status.
5.  **00:54** The generated image will appear in the "Image Preview" box.

## 3. How to Generate a Video

Once you have an image, you can bring it to life by generating a video. There are two methods.

### Method A: Simple Video Generation (Default Animation)

This method creates a short, animated video with a subtle, default motion effect.

1.  **00:56** Locate the **Movie Prompt** field below the generated image.
2.  **00:58** Leave this field blank or enter a single space. The system will use a default animation setting.
3.  **00:58** Click the magic wand icon next to the **Movie Prompt** field. The "Video Preview" box will show a "Generating..." status.
4.  **01:31** The generated video will appear.
5.  **01:35** Click on the video preview to open it in a larger window, play it, and use the three-dot menu to **Download** it (**01:45**).

### Method B: Video Generation with a Descriptive Prompt

This method gives you more control over the animation by describing the desired movement.

1.  **01:57** In the **Movie Prompt** field, describe how you want the image to animate. For example: `Whale dives deeper into the darkness below. Light fades gradually.`
2.  **02:05** Click the magic wand icon to begin generating the new video.
3.  **02:11** The new video, which follows your prompt's instructions, will be ready for preview.
4.  **02:14** Click on the video to watch the result. You will notice the whale's movement and lighting now match the prompt.
5.  **02:39** You can download the final video using the three-dot menu in the preview player.

## Key Points & Troubleshooting

*   **Image First, Then Video**: The video generation process (**Movie Prompt**) always requires a pre-existing image. It animates the generated image; it does not create a new one.
*   **Distinct Prompts**: Remember that the **Image Generation Prompt** creates the visual content, while the **Movie Prompt** directs the animation of that visual content.
*   **Provider Selection is Crucial**: If video generation fails, double-check that you have selected **Google** as the **Provider** under the **Style** > **Movie Parameters** tab.