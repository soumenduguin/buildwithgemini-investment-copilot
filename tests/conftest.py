# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from dotenv import load_dotenv

load_dotenv()

# Ensure Vertex AI environment variables are set for integration tests
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
if "GOOGLE_CLOUD_PROJECT" not in os.environ or not os.environ["GOOGLE_CLOUD_PROJECT"]:
    os.environ["GOOGLE_CLOUD_PROJECT"] = "qwiklabs-gcp-02-55287fa59349"
if "GOOGLE_CLOUD_LOCATION" not in os.environ or not os.environ["GOOGLE_CLOUD_LOCATION"]:
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
