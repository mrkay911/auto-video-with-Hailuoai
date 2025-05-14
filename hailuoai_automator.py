import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.keys import Keys

class HailuoaiAutomation:
    def __init__(self, output_folder, prompt_file, firefox_profile_path=None, headless=False):
        """
        Khởi tạo công cụ tự động hóa cho hailuoai
        
        Args:
            output_folder (str): Thư mục lưu video
            prompt_file (str): Đường dẫn đến file txt chứa prompts
            firefox_profile_path (str): Đường dẫn đến profile Firefox đã đăng nhập
            headless (bool): Chạy ở chế độ headless (không hiển thị trình duyệt)
        """
        self.output_folder = output_folder
        self.prompt_file = prompt_file
        
        # Tạo thư mục đầu ra nếu chưa tồn tại
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        # Thiết lập trình duyệt Firefox
        firefox_options = Options()
        if headless:
            firefox_options.add_argument("--headless")
        
        # Sử dụng profile đã có nếu cung cấp
        if firefox_profile_path:
            print(f"Sử dụng profile Firefox: {firefox_profile_path}")
            firefox_profile = FirefoxProfile(firefox_profile_path)
            
            # Thiết lập thư mục tải xuống vào output_folder
            firefox_profile.set_preference("browser.download.folderList", 2)
            firefox_profile.set_preference("browser.download.dir", os.path.abspath(output_folder))
            firefox_profile.set_preference("browser.download.useDownloadDir", True)
            firefox_profile.set_preference("browser.download.viewableInternally.enabledTypes", "")
            firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "video/mp4;application/x-gzip")
            
            firefox_options.profile = firefox_profile
        else:
            # Thiết lập thư mục tải xuống là output_folder
            firefox_options.set_preference("browser.download.folderList", 2)
            firefox_options.set_preference("browser.download.dir", os.path.abspath(output_folder))
            firefox_options.set_preference("browser.download.useDownloadDir", True)
            firefox_options.set_preference("browser.download.viewableInternally.enabledTypes", "")
            firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "video/mp4;application/x-gzip")
            
        # Khởi tạo trình duyệt
        self.driver = webdriver.Firefox(options=firefox_options)
        self.driver.maximize_window()
        
    def login(self, username, password):
        """
        Đăng nhập vào hailuoai
        
        Args:
            username (str): Tên đăng nhập
            password (str): Mật khẩu
        """
        print("Đang đăng nhập vào hailuoai...")
        self.driver.get("https://www.hailuoai.com/login")  # Giả định URL đăng nhập
        
        try:
            # Đợi cho form đăng nhập xuất hiện
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))  # Điều chỉnh selector phù hợp
            )
            
            # Điền thông tin đăng nhập
            self.driver.find_element(By.ID, "username").send_keys(username)
            self.driver.find_element(By.ID, "password").send_keys(password)
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            # Đợi đăng nhập thành công
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("dashboard")  # Điều chỉnh dựa trên URL sau khi đăng nhập
            )
            print("Đăng nhập thành công!")
            
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Lỗi khi đăng nhập: {e}")
            raise
    
    def navigate_to_video_creator(self):
        """Di chuyển đến trang hailuoai.video"""
        print("Đang chuyển đến trang Hailuo AI...")
        self.driver.get("https://hailuoai.video")
        
        # Hướng dẫn người dùng thực hiện các bước thủ công
        print("\n=== HƯỚNG DẪN ĐIỀU HƯỚNG THỦ CÔNG ===")
        print("1. Đợi trang tải xong")
        print("2. Nhấp vào 'Create Video' ở menu bên trái")
        print("3. Nếu cần, chuyển đến tab 'Subject Reference' hoặc tab phù hợp")
        print("4. Đặt con trỏ vào ô nhập prompt khi bạn đã sẵn sàng")
        
        input("\nKhi bạn đã hoàn thành các bước trên và đặt con trỏ vào ô nhập prompt, nhấn Enter để tiếp tục...")
        
        # Đợi một chút cho trang cập nhật
        time.sleep(2)
        print("Đã sẵn sàng tiếp tục với quá trình tự động...")
    
    def read_prompts(self):
        """Đọc các prompts từ file txt"""
        print(f"Đọc prompts từ file: {self.prompt_file}")
        try:
            with open(self.prompt_file, 'r', encoding='utf-8') as file:
                # Đọc từng dòng và lọc bỏ dòng trống
                prompts = [line.strip() for line in file.readlines() if line.strip()]
            print(f"Đã đọc {len(prompts)} prompts")
            return prompts
        except PermissionError:
            print(f"LỖI QUYỀN TRUY CẬP: Không thể đọc file {self.prompt_file}")
            print("Chương trình không có quyền đọc file prompts.")
            
            # Đề xuất giải pháp
            print("\nGIẢI PHÁP:")
            print("1. Mở Notepad với quyền Administrator")
            print("2. Tạo file prompts.txt mới")
            print("3. Nhập các prompts, mỗi prompt trên một dòng")
            
            # Tạo file tạm thời ở Desktop
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            temp_file = os.path.join(desktop_path, "hailuo_prompts_temp.txt")
            
            print(f"\nHoặc bạn có thể nhập prompts ngay bây giờ và chúng tôi sẽ lưu vào: {temp_file}")
            print("Nhập các prompts, mỗi prompt trên một dòng. Nhập 'DONE' khi hoàn thành:")
            
            prompts = []
            while True:
                line = input("> ")
                if line.strip().upper() == "DONE":
                    break
                if line.strip():
                    prompts.append(line.strip())
            
            if prompts:
                try:
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        for prompt in prompts:
                            f.write(prompt + "\n")
                    print(f"Đã lưu {len(prompts)} prompts vào {temp_file}")
                    self.prompt_file = temp_file
                except Exception as e:
                    print(f"Không thể lưu file tạm: {e}")
            
            if not prompts:
                print("Không có prompts nào được nhập. Kết thúc chương trình.")
                self.driver.quit()
                exit(1)
                
            return prompts
        except Exception as e:
            print(f"Lỗi khi đọc file prompts: {e}")
            
            # Tạo prompt trực tiếp từ input
            print("\nBạn có thể nhập prompts trực tiếp:")
            print("Nhập các prompts, mỗi prompt trên một dòng. Nhập 'DONE' khi hoàn thành:")
            
            prompts = []
            while True:
                line = input("> ")
                if line.strip().upper() == "DONE":
                    break
                if line.strip():
                    prompts.append(line.strip())
            
            if not prompts:
                print("Không có prompts nào được nhập. Kết thúc chương trình.")
                self.driver.quit()
                exit(1)
                
            return prompts
    
    def create_video(self, prompt, index):
        """
        Dán prompt và tạo video
        
        Args:
            prompt (str): Nội dung prompt
            index (int): Số thứ tự của prompt
        """
        print(f"\nĐang xử lý prompt {index}: {prompt[:50]}...")
        
        try:
            # Dán prompt vào ô đang được focus
            print("Đang dán prompt...")
            
            # Phương pháp 1: Sử dụng clipboard
            try:
                # Copy prompt vào clipboard bằng Javascript
                self.driver.execute_script(f'navigator.clipboard.writeText(`{prompt}`);')
                print("Đã copy prompt vào clipboard")
                print("Vui lòng nhấn Ctrl+V để dán prompt")
                input("Sau khi dán prompt, nhấn Enter để tiếp tục...")
            except:
                # Phương pháp 2: Nếu clipboard không hoạt động, thử phương pháp khác
                print("Không thể sử dụng clipboard. Thử phương pháp khác...")
                print(f"Vui lòng tự copy và dán prompt sau: \n\n{prompt}\n")
                input("Sau khi dán prompt, nhấn Enter để tiếp tục...")
            
            # Hướng dẫn người dùng nhấn nút tạo video
            print("\nVui lòng nhấn nút Create/Generate để tạo video")
            input("Sau khi nhấn nút tạo video, nhấn Enter để tiếp tục...")
            
            # Đợi quá trình tạo video hoàn tất
            print("Đang xử lý video, vui lòng đợi...")
            input("Khi video đã được tạo xong, nhấn Enter để tiếp tục...")
            
            # Hướng dẫn người dùng tải video
            print("\nVui lòng nhấn nút Download để tải video")
            input("Sau khi nhấn nút tải video, nhấn Enter để tiếp tục...")
            
            # Đợi file được tải xuống
            print("Đang đợi file tải xuống...")
            time.sleep(3)
            
            # Chuẩn bị cho video tiếp theo
            if index < len(self.read_prompts()):
                print(f"\nPrompt {index}/{len(self.read_prompts())} đã hoàn thành.")
                print("\nChuẩn bị cho prompt tiếp theo:")
                print("1. Quay về trạng thái sẵn sàng tạo video mới (làm mới trang hoặc nhấn nút New)")
                print("2. Đặt con trỏ vào ô nhập prompt")
                input("Khi đã sẵn sàng cho prompt tiếp theo, nhấn Enter...")
            else:
                print(f"\nĐã hoàn thành tất cả {len(self.read_prompts())} prompts!")
            
        except Exception as e:
            print(f"Lỗi trong quá trình tạo video: {e}")
            input("Gặp lỗi! Nhấn Enter để thử tiếp tục với prompt tiếp theo...")
    
    def rename_downloaded_videos(self):
        """Đổi tên các video đã tải xuống theo thứ tự"""
        print("Đang đổi tên các video đã tải xuống...")
        
        # Lấy danh sách các file trong thư mục đầu ra
        files = [f for f in os.listdir(self.output_folder) if f.endswith('.mp4')]
        files.sort(key=lambda f: os.path.getmtime(os.path.join(self.output_folder, f)))
        
        # Đổi tên các file theo thứ tự
        for i, file in enumerate(files):
            old_path = os.path.join(self.output_folder, file)
            new_name = f"video_{i+1}.mp4"
            new_path = os.path.join(self.output_folder, new_name)
            
            # Nếu file đích đã tồn tại, thêm timestamp
            if os.path.exists(new_path):
                timestamp = int(time.time())
                new_name = f"video_{i+1}_{timestamp}.mp4"
                new_path = os.path.join(self.output_folder, new_name)
            
            os.rename(old_path, new_path)
            print(f"Đổi tên: {file} -> {new_name}")
    
    def run(self, skip_login=True):
        """
        Chạy tự động toàn bộ quy trình
        
        Args:
            skip_login (bool): Bỏ qua bước đăng nhập nếu đã đăng nhập sẵn
        """
        try:
            # Di chuyển đến trang tạo video
            self.navigate_to_video_creator()
            
            # Đọc prompts
            prompts = self.read_prompts()
            
            # Hiển thị thông tin về số lượng prompts
            print(f"\nĐã tìm thấy {len(prompts)} prompts để xử lý.")
            print("Bắt đầu quy trình xử lý từng prompt...")
            
            # Tạo video cho từng prompt
            for i, prompt in enumerate(prompts, 1):
                print(f"\n=== PROMPT {i}/{len(prompts)} ===")
                print(f"Nội dung: {prompt[:100]}..." if len(prompt) > 100 else f"Nội dung: {prompt}")
                
                # Xác nhận trước khi xử lý prompt
                continue_prompt = input("Xử lý prompt này? (y/n/skip/quit): ").strip().lower()
                
                if continue_prompt == 'n' or continue_prompt == 'quit':
                    print("Dừng quy trình.")
                    break
                elif continue_prompt == 'skip':
                    print(f"Bỏ qua prompt {i}.")
                    continue
                
                # Xử lý prompt
                self.create_video(prompt, i)
                
                # Xác nhận trước khi tiếp tục với prompt tiếp theo
                if i < len(prompts):
                    continue_next = input(f"\nTiếp tục với prompt tiếp theo ({i+1}/{len(prompts)})? (y/n): ").strip().lower()
                    if continue_next != 'y':
                        print("Dừng quy trình.")
                        break
            
            # Đổi tên các video đã tải xuống
            if input("\nBạn có muốn đổi tên các video đã tải xuống? (y/n): ").strip().lower() == 'y':
                self.rename_downloaded_videos()
            
            print("\nĐã hoàn tất quy trình!")
            
        except Exception as e:
            print(f"\nLỗi trong quá trình chạy: {e}")
            input("Nhấn Enter để kết thúc...")
        finally:
            # Hỏi người dùng trước khi đóng trình duyệt
            if input("\nBạn có muốn đóng trình duyệt? (y/n): ").strip().lower() == 'y':
                print("Đóng trình duyệt...")
                self.driver.quit()
            else:
                print("Giữ trình duyệt mở. Bạn có thể đóng cửa sổ này và tiếp tục sử dụng trình duyệt.")


if __name__ == "__main__":
    # Thư mục lưu video
    OUTPUT_FOLDER = "./hailuoai_videos"
    
    # File chứa prompts
    PROMPT_FILE = "./prompts.txt"
    
    # Đường dẫn mặc định đến Firefox profile
    DEFAULT_FIREFOX_PROFILE = r"C:\Users\DuyKhanh-PC\AppData\Roaming\Mozilla\Firefox\Profiles\q82hp5tf.default-release"
    
    # Khởi động công cụ tự động hóa hailuoai
    print("=== CÔNG CỤ TỰ ĐỘNG HÓA HAILUO AI ===")
    
    # Kiểm tra đường dẫn Firefox profile
    firefox_profile = DEFAULT_FIREFOX_PROFILE
    print(f"Sử dụng Firefox profile: {firefox_profile}")
    if not os.path.exists(firefox_profile):
        print(f"Cảnh báo: Không tìm thấy profile tại: {firefox_profile}")
        use_default = input("Bạn có muốn tiếp tục với profile mặc định không? (y/n): ").strip().lower()
        if use_default != 'y':
            firefox_profile = input("Vui lòng nhập đường dẫn đến profile Firefox của bạn: ").strip()
    
    # Hỏi người dùng có muốn chạy ở chế độ headless không
    headless = False  # Mặc định không sử dụng headless
    
    # Tùy chỉnh thư mục đầu ra và file prompts
    custom_output = input(f"Nhập thư mục lưu video (Enter để sử dụng mặc định: {OUTPUT_FOLDER}): ").strip()
    if custom_output:
        OUTPUT_FOLDER = custom_output

    custom_prompt_file = input(f"Nhập đường dẫn đến file prompts (Enter để sử dụng mặc định: {PROMPT_FILE}): ").strip()
    if custom_prompt_file:
        PROMPT_FILE = custom_prompt_file
    
    # Tạo thư mục đầu ra nếu chưa tồn tại
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    # Chạy công cụ
    print("\nKhởi động trình duyệt Firefox với profile đã chọn...")
    
    try:
        automation = HailuoaiAutomation(OUTPUT_FOLDER, PROMPT_FILE, firefox_profile, headless)
        automation.run(skip_login=True)
    except Exception as e:
        print(f"\nLỗi nghiêm trọng: {e}")
        print("\nCông cụ đã gặp lỗi. Vui lòng kiểm tra lại các thông tin và thử lại.")
    finally:
        print("\nĐã hoàn thành phiên làm việc.")